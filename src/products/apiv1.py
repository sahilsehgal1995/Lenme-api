from datetime import datetime
from sqlalchemy import and_
from flask import jsonify, request, make_response, Request
from flask_security import current_user

from src import api, CustomerResource, AdminResource, OpenResource, db
from .models import Product, Rating, Description, SpecificDetails, CustomerQuestion, CustomerAnswer, Category,\
    PinCode, Taxes, ProductStock, SimilarProductMapping, Shop, ProductStockPinCode, OfferImage
from .schemas import ProductSchema, RatingSchema, DescriptionSchema, SpecificDetailsSchema, CustomerQuestionSchema, CustomerAnswerSchema, \
    CategorySchema, PinCodeSchema, TaxesSchema, SimilarProductMappingSchema, ProductStockSchema, ShopSchema, ProductStockPinCodeSchema,\
    OfferImageSchema


class CategoryResource(OpenResource):

    model = Category
    schema = CategorySchema

    def get(self, slug):

        category = self.model.query.get(slug)
        if not category:
            return make_response(jsonify({'error': 100, 'message': 'User not found'}), 404)
        category_dump = self.schema(exclude=('parent',)).dump(category).data
        db.session.commit()

        return jsonify({'success': 200, 'data': category_dump})

    def put(self, slug):

        category = self.model.query.get(slug)
        if not category:
            return make_response(jsonify({'error': 100, 'message': 'Category not found'}), 404)
        category, errors = self.schema().load(instance=category)
        if errors:
            return make_response(jsonify({'error': 101, 'message': str(errors)}), 403)
        db.session.commit()

        return jsonify({'success': 200, 'message': 'category updated successfully', 'data': self.schema().dump(category).data})

    def delete(self, slug):

        is_deleted = self.model.query.delete(slug)
        if not is_deleted:
            return make_response(jsonify({'error': 102, 'message': 'category deletion failed'}))
        db.session.commit()
        return jsonify({'success': 200, 'message': 'category deleted successfully'})


class CategoryListResource(OpenResource):

    model = Category
    schema = CategorySchema

    def get(self):
        categories = self.model.query.filter(Category.parent_id.is_(None))
        for key in request.args:
            if hasattr(self.model, key):
                values = request.args.getlist(key)
                categories = categories.filter(getattr(self.model,
                key).in_(values))
        if 'page' not in request.args:
            resources = categories.paginate(1).items
        else:
            resources = categories.paginate(int(request.args['page'])).items
        return jsonify({'success': 200, 'data': self.schema().dump(resources, many=True).data})

    def post(self):

        categories, errors = self.schema().load(request.json, session=db.session)
        if errors:
            return make_response(jsonify({'error': 101, 'message': str(errors)}), 403)
        db.session.commit()
        return jsonify({'success': 200, 'message': 'categories added successfully', 'data': self.schema().dump(categories).data})

api.add_resource(CategoryListResource, '/categories/', endpoint='categories')
api.add_resource(CategoryResource, '/category/<int:slug>/', endpoint='category')


class ProductResource(OpenResource):

    model = Product
    schema = ProductSchema

    def get(self, slug):

        product = self.model.query.get(slug)
        if not product:
            return make_response(jsonify({'error':100,
            'message': 'User not found'}), 404)
        product_dump = self.schema().dump(product).data
        db.session.commit()

        return jsonify({'success': 200, 'data': product_dump})

    def put(self, slug):

        product = self.model.query.get(slug)
        if not product:
            return make_response(jsonify({
            'error': 100, 'message': 'Product not found'
            }), 404)
        product, errors = self.schema().load(instance=product)
        if errors:
            return make_response(jsonify({
            'error': 101, 'message': str(errors)
            }), 403)
        db.session.commit()

        return jsonify({
        'success': 200, 'message': 'product updated successfully', 'data':
        self.schema().dump(product).data
        })

    def delete(self, slug):

        is_deleted = self.model.query.delete(slug)
        if not is_deleted:
            return make_response(jsonify({
            'error': 102, 'message': 'product deletion failed'
            }))
        db.session.commit()
        return jsonify({
        'success': 200, 'message': 'product deleted successfully'
        })


class ProductListResource(OpenResource):

    model = Product
    schema = ProductSchema

    def get(self):
        products = self.model.query
        for key in request.args:
            if hasattr(self.model, key):
                values = request.args.getlist(key)
                products = products.filter(getattr(self.model, key).in_(values))
        if 'page' not in request.args:
            resources = products.paginate().items
        else:
            resources = products.paginate(int(request.args['page'])).items
        return jsonify({'success': 200, 'data': self.schema().dump(resources, many=True).data})

    def post(self):

        products, errors = self.schema().load(request.json, session=db.session)
        if errors:
            return make_response(jsonify({'error': 101, 'message': str(errors)}), 403)
        db.session.add(products)
        db.session.commit()
        return jsonify({'success': 200, 'message': 'products added successfully', 'data': self.schema().dump(products).data})

api.add_resource(ProductListResource, '/products/', endpoint='products')
api.add_resource(ProductResource, '/product/<int:slug>/', endpoint='product')


class TaxesResource(OpenResource):

    model = Taxes
    schema = TaxesSchema

    def get(self, slug):

        tax = self.model.query.get(slug)
        if not tax:
            return make_response(jsonify({'error':100,
            'message': 'Tax not found'}), 404)
        tax_dump = self.schema().dump(tax).data
        db.session.commit()

        return jsonify({'success': 200, 'data':tax_dump})

    def put(self, slug):

        tax = self.model.query.get(slug)
        if not tax:
            return make_response(jsonify({
            'error': 100, 'message': 'Tax not found'
            }), 404)
        tax, errors = self.schema().load(instance=tax)
        if errors:
            return make_response(jsonify({
            'error': 101, 'message': str(errors)
            }), 403)
        db.session.commit()

        return jsonify({
        'success': 200, 'message': 'tax updated successfully', 'data':
        self.schema().dump(tax).data
        })

    def delete(self, slug):

        is_deleted = self.model.query.delete(slug)
        if not is_deleted:
            return make_response(jsonify({
            'error': 102, 'message': 'tax deletion failed'
            }))
        db.session.commit()
        return jsonify({
        'success': 200, 'message': 'tax deleted successfully'
        })


class TaxesListResource(OpenResource):

    model = Taxes
    schema = TaxesSchema

    def get(self):
        taxes = self.model.query
        for key in request.args:
            if hasattr(self.model, key):
                values = request.args.getlist(key)
                taxes = taxes.filter(getattr(self.model,
                key).in_(values))
        if 'page' not in request.args:
            resources = taxes.all()
        else:
            resources = taxes.paginate(
            int(request.args['page'])).items
        return jsonify({'success': 200, 'data':
        self.schema().dump(resources, many=True)})

    def post(self):

        taxes, errors = self.schema().load(request.json,
        session=db.session)
        if errors:
            return make_response(jsonify({'error': 101,
            'message': str(errors)}), 403)
        db.session.commit()
        return jsonify({
        'success': 200, 'message': 'taxes added successfully',
        'data': self.schema().dump(taxes).data
        })

api.add_resource(TaxesListResource, '/taxes/', endpoint='taxes')
api.add_resource(TaxesResource, '/tax/<int:slug>/', endpoint='tax')


class RatingResource(OpenResource):

    model = Rating
    schema = RatingSchema

    def get(self, slug):

        rating = self.model.query.get(slug)
        if not rating:
            return make_response(jsonify({'error':100,
            'message': 'Rating not found'}), 404)
        rating_dump = self.schema().dump(rating).data
        db.session.commit()

        return jsonify({'success': 200, 'data': rating_dump})

    def put(self, slug):

        rating = self.model.query.get(slug)
        if not rating:
            return make_response(jsonify({
            'error': 100, 'message': 'Rating not found'
            }), 404)
        rating, errors = self.schema().load(instance=rating)
        if errors:
            return make_response(jsonify({
            'error': 101, 'message': str(errors)
            }), 403)
        db.session.commit()

        return jsonify({
        'success': 200, 'message': 'rating updated successfully', 'data':
        self.schema().dump(rating).data
        })

    def delete(self, slug):

        is_deleted = self.model.query.delete(slug)
        if not is_deleted:
            return make_response(jsonify({
            'error': 102, 'message': 'rating deletion failed'
            }))
        db.session.commit()
        return jsonify({
        'success': 200, 'message': 'rating deleted successfully'
        })


class RatingListResource(OpenResource):

    model = Rating
    schema = RatingSchema

    def get(self):
        ratings = self.model.query
        for key in request.args:
            if hasattr(self.model, key):
                values = request.args.getlist(key)
                ratings = ratings.filter(getattr(self.model,
                key).in_(values))
        if 'page' not in request.args:
            resources = ratings.all()
        else:
            resources = ratings.paginate(
            int(request.args['page'])).items
        return jsonify({'success': 200, 'data':
        self.schema().dump(resources, many=True)})

    def post(self):

        ratings, errors = self.schema().load(request.json,
        session=db.session)
        if errors:
            return make_response(jsonify({'error': 101,
            'message': str(errors)}), 403)
        db.session.commit()
        return jsonify({
        'success': 200, 'message': 'ratings added successfully',
        'data': self.schema().dump(ratings).data
        })

api.add_resource(RatingListResource, '/ratings/', endpoint='ratings')
api.add_resource(RatingResource, '/rating/<int:slug>/', endpoint='rating')


class DescriptionResource(OpenResource):

    model = Description
    schema = DescriptionSchema

    def get(self, slug):

        description = self.model.query.get(slug)
        if not description:
            return make_response(jsonify({'error':100,
            'message': 'Description not found'}), 404)
        description_dump = self.schema().dump(description).data
        db.session.commit()

        return jsonify({'success': 200, 'data': description_dump})

    def put(self, slug):

        description = self.model.query.get(slug)
        if not description:
            return make_response(jsonify({
            'error': 100, 'message': 'Description not found'
            }), 404)
        description, errors = self.schema().load(instance=description)
        if errors:
            return make_response(jsonify({
            'error': 101, 'message': str(errors)
            }), 403)
        db.session.commit()

        return jsonify({
        'success': 200, 'message': 'description updated successfully', 'data':
        self.schema().dump(description).data
        })

    def delete(self, slug):

        is_deleted = self.model.query.delete(slug)
        if not is_deleted:
            return make_response(jsonify({
            'error': 102, 'message': 'description deletion failed'
            }))
        db.session.commit()
        return jsonify({
        'success': 200, 'message': 'description deleted successfully'
        })


class DescriptionListResource(OpenResource):

    model = Description
    schema = DescriptionSchema

    def get(self):
        descriptions = self.model.query
        for key in request.args:
            if hasattr(self.model, key):
                values = request.args.getlist(key)
                descriptions = descriptions.filter(getattr(self.model,
                key).in_(values))
        if 'page' not in request.args:
            resources = descriptions.all()
        else:
            resources = descriptions.paginate(
            int(request.args['page'])).items
        return jsonify({'success': 200, 'data':
        self.schema().dump(resources, many=True)})

    def post(self):

        descriptions, errors = self.schema().load(request.json,
        session=db.session)
        if errors:
            return make_response(jsonify({'error': 101,
            'message': str(errors)}), 403)
        db.session.commit()
        return jsonify({
        'success': 200, 'message': 'descriptions added successfully',
        'data': self.schema().dump(descriptions).data
        })

api.add_resource(DescriptionListResource, '/descriptions/', endpoint='descriptions')
api.add_resource(DescriptionResource, '/description/<int:slug>/', endpoint='description')


class SpecificDetailsResource(OpenResource):

    model = SpecificDetails
    schema = SpecificDetailsSchema

    def get(self, slug):

        specific_detail = self.model.query.get(slug)
        if not specific_detail:
            return make_response(jsonify({'error':100, 'message': 'SpecificDetail not found'}), 404)
        specific_detail_dump = self.schema().dump(specific_detail).data
        db.session.commit()

        return jsonify({'success': 200, 'data': specific_detail_dump})

    def put(self, slug):

        specificDetail = self.model.query.get(slug)
        if not specificDetail:
            return make_response(jsonify({
            'error': 100, 'message': 'SpecificDetail not found'
            }), 404)
        specificDetail, errors = self.schema().load(instance=specificDetail)
        if errors:
            return make_response(jsonify({
            'error': 101, 'message': str(errors)
            }), 403)
        db.session.commit()

        return jsonify({
        'success': 200, 'message': 'specificDetail updated successfully', 'data':
        self.schema().dump(specificDetail).data
        })

    def delete(self, slug):

        is_deleted = self.model.query.delete(slug)
        if not is_deleted:
            return make_response(jsonify({
            'error': 102, 'message': 'specificDetail deletion failed'
            }))
        db.session.commit()
        return jsonify({
        'success': 200, 'message': 'specificDetail deleted successfully'
        })


class SpecificDetailsListResource(OpenResource):

    model = SpecificDetails
    schema = SpecificDetailsSchema

    def get(self):
        specificDetails = self.model.query
        for key in request.args:
            if hasattr(self.model, key):
                values = request.args.getlist(key)
                specificDetails = specificDetails.filter(getattr(self.model,
                key).in_(values))
        if 'page' not in request.args:
            resources = specificDetails.all()
        else:
            resources = specificDetails.paginate(
            int(request.args['page'])).items
        return jsonify({'success': 200, 'data':
        self.schema().dump(resources, many=True)})

    def post(self):

        specificDetails, errors = self.schema().load(request.json,
        session=db.session)
        if errors:
            return make_response(jsonify({'error': 101,
            'message': str(errors)}), 403)
        db.session.commit()
        return jsonify({
        'success': 200, 'message': 'specificDetails added successfully',
        'data': self.schema().dump(specificDetails).data
        })

api.add_resource(SpecificDetailsListResource, '/specificDetails/', endpoint='specificDetails')
api.add_resource(SpecificDetailsResource, '/specificDetail/<int:slug>/', endpoint='specificDetail')


class CustomerQuestionResource(OpenResource):

    model = CustomerQuestion
    schema = CustomerQuestionSchema

    def get(self, slug):

        customerQuestion = self.model.query.get(slug)
        if not customerQuestion:
            return make_response(jsonify({'error':100,
            'message': 'Customer question not found'}), 404)
        customerQuestion_dump = self.schema().dump(customerQuestion).data
        db.session.commit()

        return jsonify({'success': 200, 'data': customerQuestion_dump})

    def put(self, slug):

        customerQuestion = self.model.query.get(slug)
        if not customerQuestion:
            return make_response(jsonify({
            'error': 100, 'message': 'Customer question not found'
            }), 404)
        customerQuestion, errors = self.schema().load(instance=customerQuestion)
        if errors:
            return make_response(jsonify({
            'error': 101, 'message': str(errors)
            }), 403)
        db.session.commit()

        return jsonify({
        'success': 200, 'message': 'customerQuestion updated successfully', 'data':
        self.schema().dump(customerQuestion).data
        })

    def delete(self, slug):

        is_deleted = self.model.query.delete(slug)
        if not is_deleted:
            return make_response(jsonify({
            'error': 102, 'message': 'customerQuestion deletion failed'
            }))
        db.session.commit()
        return jsonify({
        'success': 200, 'message': 'customerQuestion deleted successfully'
        })


class CustomerQuestionListResource(OpenResource):

    model = CustomerQuestion
    schema = CustomerQuestionSchema

    def get(self):
        customerQuestions = self.model.query
        for key in request.args:
            if hasattr(self.model, key):
                values = request.args.getlist(key)
                customerQuestions = customerQuestions.filter(getattr(self.model,
                key).in_(values))
        if 'page' not in request.args:
            resources = customerQuestions.all()
        else:
            resources = customerQuestions.paginate(
            int(request.args['page'])).items
        return jsonify({'success': 200, 'data':
        self.schema().dump(resources, many=True)})

    def post(self):

        customerQuestions, errors = self.schema().load(request.json,
        session=db.session)
        if errors:
            return make_response(jsonify({'error': 101,
            'message': str(errors)}), 403)
        db.session.commit()
        return jsonify({
        'success': 200, 'message': 'Customer questions added successfully',
        'data': self.schema().dump(customerQuestions).data
        })

api.add_resource(CustomerQuestionListResource, '/customerQuestions/', endpoint='customerQuestions')
api.add_resource(CustomerQuestionResource, '/customerQuestion/<int:slug>/', endpoint='customerQuestion')


class CustomerAnswerResource(OpenResource):

    model = CustomerAnswer
    schema = CustomerAnswerSchema

    def get(self, slug):

        customerAnswer = self.model.query.get(slug)
        if not customerAnswer:
            return make_response(jsonify({'error':100,
            'message': 'Customer answer not found'}), 404)
        customerAnswer_dump = self.schema().dump(customerAnswer).data
        db.session.commit()

        return jsonify({'success': 200, 'data': customerAnswer_dump})

    def put(self, slug):

        customerAnswer = self.model.query.get(slug)
        if not customerAnswer:
            return make_response(jsonify({
            'error': 100, 'message': 'Customer answer availability not found'
            }), 404)
        customerAnswer, errors = self.schema().load(instance=customerAnswer)
        if errors:
            return make_response(jsonify({
            'error': 101, 'message': str(errors)
            }), 403)
        db.session.commit()

        return jsonify({
        'success': 200, 'message': 'Customer answer updated successfully', 'data':
        self.schema().dump(customerAnswer).data
        })

    def delete(self, slug):

        is_deleted = self.model.query.delete(slug)
        if not is_deleted:
            return make_response(jsonify({
            'error': 102, 'message': 'Customer answer deletion failed'
            }))
        db.session.commit()
        return jsonify({
        'success': 200, 'message': 'Customer answer deleted successfully'
        })


class CustomerAnswerListResource(OpenResource):

    model = CustomerAnswer
    schema = CustomerAnswerSchema

    def get(self):
        customerAnswers = self.model.query
        for key in request.args:
            if hasattr(self.model, key):
                values = request.args.getlist(key)
                customerAnswers = customerAnswers.filter(getattr(self.model,
                key).in_(values))
        if 'page' not in request.args:
            resources = customerAnswers.all()
        else:
            resources = customerAnswers.paginate(
            int(request.args['page'])).items
        return jsonify({'success': 200, 'data':
        self.schema().dump(resources, many=True)})

    def post(self):

        customerAnswers, errors = self.schema().load(request.json,
        session=db.session)
        if errors:
            return make_response(jsonify({'error': 101,
            'message': str(errors)}), 403)
        db.session.commit()
        return jsonify({
        'success': 200, 'message': 'Customer answers added successfully',
        'data': self.schema().dump(customerAnswers).data
        })

api.add_resource(CustomerAnswerListResource, '/customerAnswers/', endpoint='customerAnswers')
api.add_resource(CustomerAnswerResource, '/customerAnswer/<int:slug>/', endpoint='customerAnswer')


class PinCodeResource(OpenResource):

    model = PinCode
    schema = PinCodeSchema

    def get(self, slug):

        pin_code = self.model.query.get(slug)
        if not pin_code:
            return make_response(jsonify({'error':100,
            'message': 'Pincode not found'}), 404)
        pin_code_dump = self.schema().dump(pin_code).data
        db.session.commit()

        return jsonify({'success': 200, 'data': pin_code_dump})

    def put(self, slug):

        pin_code = self.model.query.get(slug)
        if not pin_code:
            return make_response(jsonify({
            'error': 100, 'message': 'Pincode not found'
            }), 404)
        pin_code, errors = self.schema().load(instance=pin_code)
        if errors:
            return make_response(jsonify({
            'error': 101, 'message': str(errors)
            }), 403)
        db.session.commit()

        return jsonify({
        'success': 200, 'message': 'Pincode updated successfully', 'data':
        self.schema().dump(pin_code).data
        })

    def delete(self, slug):

        is_deleted = self.model.query.delete(slug)
        if not is_deleted:
            return make_response(jsonify({
            'error': 102, 'message': 'Pincode deletion failed'
            }))
        db.session.commit()
        return jsonify({
        'success': 200, 'message': 'Pincode deleted successfully'
        })


class PinCodeListResource(OpenResource):

    model = PinCode
    schema = PinCodeSchema

    def get(self):
        pin_codes = self.model.query
        for key in request.args:
            if hasattr(self.model, key):
                values = request.args.getlist(key)
                pin_codes = pin_codes.filter(getattr(self.model,
                key).in_(values))
        if 'page' not in request.args:
            resources = pin_codes.all()
        else:
            resources = pin_codes.paginate(
            int(request.args['page'])).items
        return jsonify({'success': 200, 'data':
        self.schema().dump(resources, many=True)})

    def post(self):

        pin_codes, errors = self.schema().load(request.json,
        session=db.session)
        if errors:
            return make_response(jsonify({'error': 101,
            'message': str(errors)}), 403)
        db.session.commit()
        return jsonify({
        'success': 200, 'message': 'Pincodes added successfully',
        'data': self.schema().dump(pin_codes).data
        })

api.add_resource(PinCodeListResource, '/pin_codes/', endpoint='pin_codes')
api.add_resource(PinCodeResource, '/pin_code/<int:slug>/', endpoint='pin_code')


class ProductStockResource(OpenResource):
    model = ProductStock
    schema = ProductStockSchema

    def get(self, slug):
        pin_code = request.args['pinCode']
        product_id = request.args['productId']

        stocks = self.model.query.join(PinCode, ProductStock.pin_codes).\
            filter(ProductStock.product_id == product_id, PinCode.pin_code == pin_code).first()
        if stocks:
            return jsonify({'success': True, 'stocks': stocks.stock})
        return jsonify({'success': True, 'stocks': 0})

    def put(self, slug):

        stock = self.model.query.get(slug)
        stock, errors = self.schema().load(request.json, instance=stock)
        if errors:
            return make_response(jsonify({'error': True, 'data': errors}))
        db.session.commit()
        return jsonify({'success': 200, 'data': self.schema().dump(stock).data})


api.add_resource(ProductStockResource, '/stock/<slug>/', endpoint='stock')


class ProductStockListResource(AdminResource):
    model = ProductStock
    schema = ProductStockSchema

    def get(self):

        stocks = self.model.query.filter(ProductStock.shop_id == current_user.shop.id)
        for key in request.args:
            if hasattr(self.model, key):
                values = request.args.getlist(key)
                stocks = stocks.filter(getattr(self.model, key) == values)
        count = stocks.count()
        per_page = int(request.args['perPage']) if 'perPage' in request.args else 20
        page = int(request.args['page']) if 'page' in request.args else 1
        resources = stocks.paginate(page, per_page=per_page).items
        return jsonify({'success': 200, 'data': self.schema().dump(resources, many=True).data, 'count': count})

api.add_resource(ProductStockListResource, '/stocks/', endpoint='stocks')


class ShopResource(AdminResource):
    model = Shop
    schema = ShopSchema

    def get(self):

        products = Product.query.join(ProductStock, and_(ProductStock.product_id == Product.id))\
            .filter(and_(ProductStock.stock > 0, ProductStock.shop_id == current_user.shop.id)).all()
        return jsonify({'success': 200, 'shop': self.schema().dump(current_user.shop).data,
                        'products': ProductSchema(exclude=('mrp', 'price', 'similar_quantity_products', 'product_stocks',
                                                           'base_category', 'grand_parent_category', 'is_bulk_discounted', 'parent_category',
                                                           'all_categories', 'brand_name', 'brand_id')).dump(products, many=True).data})

api.add_resource(ShopResource, '/store/', endpoint='store')


class ShopListResource(AdminResource):
    model = Shop
    schema = ShopSchema

    def get(self):

        shops = self.model.query
        for key in request.args:
            if hasattr(self.model, key):
                values = request.args.getlist(key)
                shops = shops.filter(getattr(self.model, key) == values)
        count = shops.count()
        per_page = int(request.args['perPage']) if 'perPage' in request.args else 20
        page = int(request.args['page']) if 'page' in request.args else 1
        resources = shops.paginate(page, per_page=per_page).items
        return jsonify({'success': 200, 'data': self.schema().dump(resources, many=True).data, 'count': count})

api.add_resource(ShopListResource, '/stores/', endpoint='stores')


class SimilarProductMappingResource(OpenResource):

    model = SimilarProductMapping
    schema = SimilarProductMappingSchema

    def get(self, slug):

        similar_products = self.model.query.filter(self.model.product_id == slug).all()
        if similar_products:
            return jsonify({'success': True, 'data': self.schema().dump(similar_products, many=True).data})
        return jsonify({'error': True})

api.add_resource(SimilarProductMappingResource, '/similar_products/<int:slug>/', endpoint='similar_products')


class ProductStockPinCodeResource(OpenResource):
    model = ProductStockPinCode
    schema = ProductStockPinCodeSchema

    def get(self):
        pin_code = request.args['pinCode']
        product_id = request.args['productId']

        stocks = self.model.query.join(PinCode, and_(PinCode.id == self.model.pin_code_id))\
            .join(ProductStock, and_(ProductStock.id == ProductStockPinCode.product_stock_id)).\
            filter(ProductStock.product_id == product_id, PinCode.pin_code == pin_code).first()

        if stocks:
            return jsonify({'success': True, 'stocks': stocks.stocks.stock})
        return jsonify({'success': True, 'stocks': 0})

api.add_resource(ProductStockPinCodeResource, '/product_stock_pin_code/', endpoint='product_stock_pin_code')


class ShopProductListResource(AdminResource):
    model = Product
    schema = ProductSchema

    def get(self):

        products = self.model.query.join(ProductStock, and_(ProductStock.product_id == Product.id))\
            .filter(ProductStock.shop_id == current_user.shop.id)
        products = products.all()
        return jsonify({'success': 200, 'data': self.schema(exclude=('images', 'description', 'similar_quantity_products',
                                                                     'rates', 'product_stocks')).dump(products, many=True).data})

api.add_resource(ShopProductListResource, '/stores/products/', endpoint='shop_products')


class OfferImageListResource(OpenResource):
    model = OfferImage
    schema = OfferImageSchema

    def get(self):

        offers = self.model.query.filter(self.model.expiry > datetime.now()).all()
        return jsonify({'success': 200, 'data': self.schema().dump(offers, many=True).data})

api.add_resource(OfferImageListResource, '/offer-images/', endpoint='offer_images')
