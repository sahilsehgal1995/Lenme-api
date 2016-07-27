from random import randint
from sqlalchemy import and_
from sqlalchemy.exc import OperationalError, IntegrityError
from flask_security import current_user
from flask import jsonify, request, make_response
from src import api, CustomerResource, OpenResource, AdminResource, db
from .models import Order, OrderedProduct, OrderTaxes, SavedCard, Status, OrderLog, DeliveryBoy, UserCart
from .schemas import OrderSchema, OrderedProductSchema, OrderTaxesSchema, SavedCardSchema, StatusSchema,\
    OrderLogSchema, DeliveryBoySchema, UserCartSchema
from src.products.models import ProductStock, PinCode, ProductStockPinCode, Product


class OrderResource(CustomerResource):

    model = Order
    schema = OrderSchema

    def get(self, slug):

        order = self.model.query.get(slug)
        if not order:
            return make_response(jsonify({'error': 100, 'message': 'Order not found'}), 404)
        order_dump = self.schema().dump(order).data
        db.session.commit()

        return jsonify({'success': 200, 'data':order_dump})

    def put(self, slug):
        print(current_user,current_user.id,current_user.roles)
        order = self.model.query.get(slug)
        if not order:
            return make_response(jsonify({'error': 100, 'message': 'Order not found'}), 404)
        if current_user.has_role('delivery_boy'):
            if request.json['otp'] == order.otp:
                order.status = 'delivered'
                db.session.commit()
                return jsonify({'success': 200, 'message': 'order delivered',
                                'data': self.schema().dump(order).data})
            else:
                return make_response(jsonify({'error': 100, 'message': 'Order not found'}), 404)
        order, errors = self.schema().load(request.json, instance=order)
        if errors:
            return make_response(jsonify({'error': 101, 'message': str(errors)}), 403)
        db.session.commit()

        return jsonify({'success': 200, 'message': 'order updated successfully',
                        'data': self.schema().dump(order).data})

    def delete(self, slug):

        is_deleted = self.model.query.delete(slug)
        if not is_deleted:
            return make_response(jsonify({'error': 102, 'message': 'order deletion failed'}))
        db.session.commit()

        return jsonify({'success': 200, 'message': 'order deleted successfully'})


class OrderListResource(CustomerResource):

    model = Order
    schema = OrderSchema

    def get(self):

        if current_user.has_role('customer'):
            orders = self.model.query.filter(self.model.user_id == current_user.id)
        elif current_user.has_role('delivery_boy'):
            orders = self.model.query.filter(self.model.delivery_boy_id == current_user.delivery_boy[0].id)
        else:
            orders = self.model.query.join(OrderedProduct, and_(OrderedProduct.order_id == self.model.id))\
                .filter(OrderedProduct.shop_id == current_user.shop.id)

        for key in request.args:
            if hasattr(self.model, key):
                values = request.args.getlist(key)
                if key == 'created_on':
                    orders = orders.filter(Order.created_on.between(values[0], values[1]))
                else:
                    orders = orders.filter(getattr(self.model, key).in_(values))

        count = orders.count()
        per_page = int(request.args['perPage']) if 'perPage' in request.args else 20
        if 'page' not in request.args:
            page = 1
        else:
            page = int(request.args['page'])
        orders = orders.order_by(-Order.id)
        resources = orders.paginate(page, per_page=per_page).items
        return jsonify({'success': 200, 'data': self.schema().dump(resources, many=True).data, 'count': count})

    def post(self):

        try:

            data = request.json
            pin_code = data['pinCode']
            items = data.pop('items')
            saved_cart_id = data.pop('saved_cart_id') if 'saved_cart_id' in data and data['saved_cart_id'] else None
            if saved_cart_id:
                cart = UserCart.query.get(saved_cart_id)
                if cart:
                    db.session.delete(cart)
                    db.session.commit()

            coupon = data.pop('coupon') if 'coupon' in data and data['coupon']['id'] else None
            for item in items:
                stock = ProductStock.query.join(ProductStockPinCode). \
                    filter(ProductStock.product_id == item['id'], PinCode.pin_code == pin_code).first()

                if stock.stock < item['quantity']:
                    return jsonify({'error': True, 'message': 'Stock finished for ' + item['name'], 'item': item['id']})
                stock.stock = stock.stock - item['quantity']
                item['shop_id'] = stock.shop_id
                db.session.commit()
            order_data = data
            order_data['otp'] = randint(1000, 9999)
            order_data['sub_total'] = data['subTotal']
            order_data['delivery_charge'] = data['shipping']
            order_data['delivery_instructions'] = data['delivery_instructions']
            order_data['convenience_charge'] = data['convenience_charge']

            if coupon:
                order_data['coupon_id'] = coupon['id']
                order_data['discount'] = coupon['value']
            orders, errors = self.schema().load(order_data, session=db.session)
            if errors:
                return make_response(jsonify({'error': 101, 'message': str(errors)}), 403)
            db.session.add(orders)
            db.session.commit()
            for item in items:
                taxes = item.pop('taxes')
                item['product_id'] = item['id']
                item['order_id'] = orders.id
                item.pop('id')
                product, errors = OrderedProductSchema().load(item, session=db.session)
                db.session.add(product)
                db.session.commit()

                for tax in taxes:
                    tax['order_product_id'] = product.id
                    tax['tax_id'] = tax['id']
                    tax.pop('id')
                    t, errors = OrderTaxesSchema().load(tax, session=db.session)
                    db.session.add(t)
                    db.session.commit()
        except (KeyError, ValueError, TypeError, OperationalError, IntegrityError) as e:
            db.session.rollback()
            return make_response(jsonify({'error': True, 'data': str(e)}), 403)
        from src.mailer.emailer import send_order_email
        order_data = self.schema().dump(orders).data
        order_data['pin_code'] = pin_code
        send_order_email(order_data)
        return jsonify({'success': 200, 'message': 'orders added successfully', 'data': order_data})

api.add_resource(OrderListResource, '/orders/', endpoint='orders')
api.add_resource(OrderResource, '/order/<int:slug>/', endpoint='order')


class OrderedProductResource(OpenResource):

    model = OrderedProduct
    schema = OrderedProductSchema

    def get(self, slug):

        ordered_product = self.model.query.get(slug)
        if not ordered_product:
            return make_response(jsonify({'error':100, 'message': 'Ordered product not found'}), 404)
        ordered_product_dump = self.schema().dump(ordered_product).data
        db.session.commit()

        return jsonify({'success': 200, 'data':ordered_product_dump})

    def put(self, slug):

        ordered_product = self.model.query.get(slug)
        if not ordered_product:
            return make_response(jsonify({'error': 100, 'message': 'Ordered product not found'}), 404)
        ordered_product, errors = self.schema().load(instance=ordered_product)
        if errors:
            return make_response(jsonify({'error': 101, 'message': str(errors)}), 403)
        db.session.commit()

        return jsonify({'success': 200, 'message': 'Ordered product updated successfully',
                        'data': self.schema().dump(ordered_product).data})

    def delete(self, slug):

        is_deleted = self.model.query.delete(slug)
        if not is_deleted:
            return make_response(jsonify({'error': 102, 'message': 'Ordered product deletion failed'}))
        db.session.commit()

        return jsonify({'success': 200, 'message': 'Ordered product deleted successfully'})


class OrderedProductListResource(OpenResource):

    model = OrderedProduct
    schema = OrderedProductSchema

    def get(self):

        ordered_products = self.model.query
        for key in request.args:
            if hasattr(self.model, key):
                values = request.args.getlist(key)
                ordered_products = ordered_products.filter(getattr(self.model, key).in_(values))
        if 'page' not in request.args:
            resources = ordered_products.all()
        else:
            resources = ordered_products.paginate(int(request.args['page'])).items

        return jsonify({'success': 200, 'data': self.schema().dump(resources, many=True)})

    def post(self):

        ordered_products, errors = self.schema().load(request.json, session=db.session)
        if errors:
            return make_response(jsonify({'error': 101, 'message': str(errors)}), 403)
        db.session.commit()

        return jsonify({'success': 200, 'message': 'Ordered products added successfully',
                        'data': self.schema().dump(ordered_products).data})

api.add_resource(OrderedProductListResource, '/ordered_products/', endpoint='ordered_products')
api.add_resource(OrderedProductResource, '/ordered_product/<int:slug>/', endpoint='ordered_product')


class OrderTaxesResource(OpenResource):

    model = OrderTaxes
    schema = OrderTaxesSchema

    def get(self, slug):

        order_tax = self.model.query.get(slug)
        if not order_tax:
            return make_response(jsonify({'error':100, 'message': 'Order tax not found'}), 404)
        order_tax_dump = self.schema().dump(order_tax).data
        db.session.commit()

        return jsonify({'success': 200, 'data':order_tax_dump})

    def put(self, slug):

        order_tax = self.model.query.get(slug)
        if not order_tax:
            return make_response(jsonify({'error': 100, 'message': 'Order tax not found'}), 404)
        order_tax, errors = self.schema().load(instance=order_tax)
        if errors:
            return make_response(jsonify({'error': 101, 'message': str(errors)}), 403)
        db.session.commit()

        return jsonify({'success': 200, 'message': 'Order tax updated successfully',
                        'data': self.schema().dump(order_tax).data})

    def delete(self, slug):

        is_deleted = self.model.query.delete(slug)
        if not is_deleted:
            return make_response(jsonify({'error': 102, 'message': 'Order tax deletion failed'}))
        db.session.commit()

        return jsonify({'success': 200, 'message': 'Order tax deleted successfully'})


class OrderTaxesListResource(OpenResource):

    model = OrderTaxes
    schema = OrderTaxesSchema

    def get(self):

        order_taxes = self.model.query
        for key in request.args:
            if hasattr(self.model, key):
                values = request.args.getlist(key)
                order_taxes = order_taxes.filter(getattr(self.model, key).in_(values))
        if 'page' not in request.args:
            resources = order_taxes.all()
        else:
            resources = order_taxes.paginate(int(request.args['page'])).items

        return jsonify({'success': 200, 'data': self.schema().dump(resources, many=True)})

    def post(self):

        order_taxes, errors = self.schema().load(request.json, session=db.session)
        if errors:
            return make_response(jsonify({'error': 101, 'message': str(errors)}), 403)
        db.session.commit()

        return jsonify({'success': 200, 'message': 'Order taxes added successfully',
                        'data': self.schema().dump(order_taxes).data})

api.add_resource(OrderTaxesListResource, '/order_taxes/', endpoint='order_taxes')
api.add_resource(OrderTaxesResource, '/order_tax/<int:slug>/', endpoint='order_tax')


class SavedCardResource(OpenResource):

    model = SavedCard
    schema = SavedCardSchema

    def get(self, slug):

        saved_card = self.model.query.get(slug)
        if not saved_card:
            return make_response(jsonify({'error': 100, 'message': 'saved_card not found'}), 404)
        saved_card_dump = self.schema().dump(saved_card).data
        db.session.commit()

        return jsonify({'success': 200, 'data': saved_card_dump})

    def put(self, slug):

        saved_card = self.model.query.get(slug)
        if not saved_card:
            return make_response(jsonify({'error': 100, 'message': 'saved_card not found'}), 404)
        saved_card, errors = self.schema().load(instance=saved_card)
        if errors:
            return make_response(jsonify({'error': 101, 'message': str(errors)}), 403)
        db.session.commit()

        return jsonify({'success': 200, 'message': 'saved card updated successfully',
                        'data': self.schema().dump(saved_card).data})

    def delete(self, slug):

        is_deleted = self.model.query.delete(slug)
        if not is_deleted:
            return make_response(jsonify({'error': 102, 'message': 'saved_card deletion failed'}))
        db.session.commit()

        return jsonify({'success': 200, 'message': 'saved_card deleted successfully'})


class SavedCardListResource(OpenResource):

    model = SavedCard
    schema = SavedCardSchema

    def get(self):

        saved_cards = self.model.query
        for key in request.args:
            if hasattr(self.model, key):
                values = request.args.getlist(key)
                saved_cards = saved_cards.filter(getattr(self.model, key).in_(values))
        if 'page' not in request.args:
            resources = saved_cards.all()
        else:
            resources = saved_cards.paginate(int(request.args['page'])).items

        return jsonify({'success': 200, 'data':self.schema().dump(resources, many=True)})

    def post(self):

        saved_cards, errors = self.schema().load(request.json,
        session=db.session)
        if errors:
            return make_response(jsonify({'error': 101, 'message': str(errors)}), 403)
        db.session.commit()

        return jsonify({'success': 200, 'message': 'saved_cards added successfully',
                        'data': self.schema().dump(saved_cards).data})

api.add_resource(SavedCardListResource, '/saved_cards/', endpoint='saved_cards')
api.add_resource(SavedCardListResource, '/saved_card/<int:slug>/', endpoint='saved_card')


class StatusResource(OpenResource):

    model = Status
    schema = StatusSchema

    def get(self, slug):

        status = self.model.query.get(slug)
        if not status:
            return make_response(jsonify({'error':100, 'message': 'Status not found'}), 404)
        status_dump = self.schema().dump(status).data
        db.session.commit()

        return jsonify({'success': 200, 'data':status_dump})

    def put(self, slug):

        status = self.model.query.get(slug)
        if not status:
            return make_response(jsonify({
            'error': 100, 'message': 'Status not found'
            }), 404)
        status, errors = self.schema().load(instance=status)
        if errors:
            return make_response(jsonify({ 'error': 101, 'message': str(errors) }), 403)
        db.session.commit()

        return jsonify({ 'success': 200, 'message': 'status updated successfully',
                        'data':self.schema().dump(status).data })

    def delete(self, slug):

        is_deleted = self.model.query.delete(slug)
        if not is_deleted:
            return make_response(jsonify({ 'error': 102, 'message': 'status deletion failed'}))
        db.session.commit()
        return jsonify({'success': 200, 'message': 'status deleted successfully'})


class StatusListResource(OpenResource):

    model = Status
    schema = StatusSchema

    def get(self):

        status = self.model.query
        for key in request.args:
            if hasattr(self.model, key):
                values = request.args.getlist(key)
                status = status.filter(getattr(self.model, key).in_(values))
        if 'page' not in request.args:
            resources = status.all()
        else:
            resources = status.paginate(int(request.args['page'])).items

        return jsonify({'success': 200, 'data':self.schema().dump(resources, many=True)})

    def post(self):

        status, errors = self.schema().load(request.json, session=db.session)
        if errors:
            return make_response(jsonify({'error': 101, 'message': str(errors)}), 403)
        db.session.commit()

        return jsonify({'success': 200, 'message': 'status added successfully',
                        'data': self.schema().dump(status).data})

api.add_resource(StatusListResource, '/status/', endpoint='status')
api.add_resource(StatusResource, '/status/<int:slug>/', endpoint='statuses')


class OrderLogResource(OpenResource):

    model = OrderLog
    schema = OrderLogSchema

    def get(self, slug):

        order_log = self.model.query.get(slug)
        if not order_log:
            return make_response(jsonify({'error' : 100, 'message': 'Order log not found'}), 404)
        order_log_dump = self.schema().dump(order_log).data
        db.session.commit()

        return jsonify({'success': 200, 'data': order_log_dump})

    def put(self, slug):

        order_log = self.model.query.get(slug)
        if not order_log:
            return make_response(jsonify({'error': 100, 'message': 'Order log not found'}), 404)
        order_log, errors = self.schema().load(instance=order_log)
        if errors:
            return make_response(jsonify({'error': 101, 'message': str(errors)}), 403)
        db.session.commit()

        return jsonify({'success': 200, 'message': 'order_log updated successfully',
                        'data':self.schema().dump(order_log).data})

    def delete(self, slug):

        is_deleted = self.model.query.delete(slug)
        if not is_deleted:
            return make_response(jsonify({
            'error': 102, 'message': 'order log deletion failed'
            }))
        db.session.commit()

        return jsonify({'success': 200, 'message': 'order log deleted successfully'})


class OrderLogListResource(OpenResource):

    model = OrderLog
    schema = OrderLogSchema

    def get(self):
        order_logs = self.model.query
        for key in request.args:
            if hasattr(self.model, key):
                values = request.args.getlist(key)
                order_logs = order_logs.filter(getattr(self.model, key).in_(values))
        if 'page' not in request.args:
            resources = order_logs.all()
        else:
            resources = order_logs.paginate(int(request.args['page'])).items

        return jsonify({'success': 200, 'data':self.schema().dump(resources, many=True)})

    def post(self):

        order_logs, errors = self.schema().load(request.json,
        session=db.session)
        if errors:
            return make_response(jsonify({'error': 101, 'message': str(errors)}), 403)
        db.session.commit()

        return jsonify({'success': 200, 'message': 'order logs added successfully',
                        'data': self.schema().dump(order_logs).data})

api.add_resource(OrderLogListResource, '/order_logs/', endpoint='order_logs')
api.add_resource(OrderLogResource, '/order_log/<int:slug>/', endpoint='order_log')


class DeliveryBoyListResource(OpenResource):

    model = DeliveryBoy
    schema = DeliveryBoySchema

    def get(self):
        return jsonify({'success': True, 'data': self.schema().dump(self.model.query.all(), many=True).data})

api.add_resource(DeliveryBoyListResource, '/delivery_boys/', endpoint='delivery_boys')


class ShopOrderListResource(AdminResource):

    model = Order
    schema = OrderSchema

    def post(self):

        try:

            data = request.json
            items = data.pop('items')
            coupon = data.pop('coupon') if 'coupon' in data and data['coupon']['id'] else None
            for item in items:
                stock = ProductStock.query.join(Product). \
                    filter(ProductStock.product_id == item['id'], ProductStock.shop_id == current_user.shop.id).first()
                stock.stock = stock.stock - item['quantity']
                if stock.stock < 0:
                    return jsonify({'error': True, 'message': 'Stock finished for ' + item['name'], 'item': item['id']})
                item['shop_id'] = stock.shop_id
                db.session.commit()
            order_data = data
            order_data['sub_total'] = data['subTotal']
            order_data['delivery_charge'] = data['shipping']
            if coupon:
                order_data['coupon_id'] = coupon['id']
                order_data['discount'] = coupon['value']
            orders, errors = self.schema().load(order_data, session=db.session)
            if errors:
                return make_response(jsonify({'error': 101, 'message': str(errors)}), 403)
            db.session.add(orders)
            db.session.commit()
            for item in items:
                taxes = item.pop('taxes')
                item['product_id'] = item['id']
                item['order_id'] = orders.id
                item.pop('id')
                product, errors = OrderedProductSchema().load(item, session=db.session)
                db.session.add(product)
                db.session.commit()

                for tax in taxes:
                    tax['order_product_id'] = product.id
                    tax['tax_id'] = tax['id']
                    tax.pop('id')
                    t, errors = OrderTaxesSchema().load(tax, session=db.session)
                    db.session.add(t)
                    db.session.commit()
        except (KeyError, ValueError, TypeError, OperationalError, IntegrityError) as e:
            db.session.rollback()
            return make_response(jsonify({'error': True, 'data': str(e)}), 403)
        order_data = self.schema().dump(orders).data
        return jsonify({'success': 200, 'message': 'orders added successfully', 'data': order_data})

api.add_resource(ShopOrderListResource, '/shop-orders/', endpoint='shop-orders')


class UserCartListResource(CustomerResource):

    model = UserCart
    schema = UserCartSchema

    def post(self):
        data = request.json
        items = data.pop('saved_cart_items')
        data['user_cart_items'] = []
        for item in items:
            data['user_cart_items'].append({'product_id': item['id']})
        saved_cart, errors = self.schema().load(data, session=db.session)
        if errors:
            return make_response(jsonify({'error': True, 'message': str(errors)}), 403)
        db.session.add(saved_cart)
        db.session.commit()
        return jsonify({'success': True, 'data': saved_cart.id})

api.add_resource(UserCartListResource, '/saved-cart/', endpoint='saved_cart')
