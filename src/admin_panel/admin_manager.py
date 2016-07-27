import os.path as op
import src.admin_panel as admin_module
from flask import render_template, request, redirect, flash
from flask_admin.base import expose
from flask_admin.contrib import sqla
from flask_admin.contrib.fileadmin import FileAdmin
from flask_excel import make_response_from_query_sets
from pyexcel_xlsx import xlsx
from flask_security import login_required, current_user
from src import admin, db
from src.admin_panel.models import Log
from src.admin_panel.schemas import LogSchema
from src.orders.models import Order, OrderedProduct, OrderTaxes, DeliveryBoy, UserCartItem, UserCart
from src.products.models import Category, Brand, Product, Rating, Taxes, \
    CustomerQuestion, CustomerAnswer, CustomerAnswerImages, PinCode, SpecificDetails, Description, ProductImage, ProductQuantityMapping, \
    SimilarProductMapping, Shop, ProductStock, ProductStockPinCode, OfferImage, ProductRate
from src.user.models import User, UserProfile, Role, Address, Locality, City, CouponUserMapping, Coupon
from src.elasticsearch.elastic_manager import  ElasticSearchManager


@login_required
def index():
    return render_template('index.html')


class MyModel(sqla.ModelView):
    column_display_pk = True
    column_exclude_list = ('shop_stocks',)

    @expose('/export')
    def export_excel(self):
        columns = [i.name for i in self.model.__table__.columns]
        query = self.model.query.slice(int(request.args['startIndex']), int(request.args['endIndex']))
        return make_response_from_query_sets(query_sets=query, column_names=columns,
                                             file_type='xlsx', status=200, file_name=self.model.__name__)

    @expose('/import', methods=['POST'])
    def import_excel(self):
        schema = getattr(admin_module, self.model.__name__ + 'Schema')

        def product_init(row):

            log, errors = LogSchema().load({'owner_id': current_user.id, 'updated_data': row, 'action': 'data update by excel',
                                            'updated_model': self.model.__name__})
            if errors:
                return True
            db.session.add(log)
            db.session.commit()
            if row['id']:
                p = self.model.query.get(row['id'])
                if p:
                    p, errors = schema().load(row, instance=self.model.query.get(row['id']))
                    if errors:
                        print(errors)
                        return False
                    db.session.commit()

                else:
                    print(row)
                    p, errors = schema().load(row, session=db.session)
                    if errors:
                        print(errors)
                        return False
                    db.session.add(p)
                    db.session.commit()

            else:
                p, errors = schema().load(row, session=db.session)
                if errors:
                    print(errors)
                    return False
                db.session.add(p)
                db.session.commit()
            if self.model.__name__ == 'Product':
                ElasticSearchManager().index_product(p.id)
            return p

        request.save_to_database(field_name='files', session=db.session, table=self.model, initializer=product_init)
        flash('Uploaded Successfully')
        return redirect(self.url)

    def on_model_change(self, form, model, is_created):
        log, errors = LogSchema().load({'owner_id': current_user.id, 'updated_data': form.data, 'action': 'data update in admin',
                                        'updated_model': self.model.__name__})
        if errors:
            return True
        db.session.add(log)
        db.session.commit()

    def after_model_change(self, form, model, is_created):
        if self.model.__name__ == 'Product':
            ElasticSearchManager().index_product(model.id)

    def is_accessible(self):
        return current_user.has_role('admin')

    list_template = 'list_template.html'


admin.add_view(MyModel(User, session=db.session))
admin.add_view(MyModel(UserProfile, session=db.session))
admin.add_view(MyModel(Role, session=db.session))
admin.add_view(MyModel(Coupon, session=db.session))
admin.add_view(MyModel(CouponUserMapping, session=db.session))

admin.add_view(MyModel(Product, session=db.session))
admin.add_view(MyModel(Category, session=db.session))
admin.add_view(MyModel(Brand, session=db.session))
admin.add_view(MyModel(Rating, session=db.session))
admin.add_view(MyModel(Taxes, session=db.session))

admin.add_view(MyModel(CustomerQuestion, session=db.session))
admin.add_view(MyModel(CustomerAnswer, session=db.session))
admin.add_view(MyModel(CustomerAnswerImages, session=db.session))
admin.add_view(MyModel(PinCode, session=db.session))
admin.add_view(MyModel(SpecificDetails, session=db.session))
admin.add_view(MyModel(Description, session=db.session))
admin.add_view(MyModel(ProductImage, session=db.session))
admin.add_view(MyModel(ProductQuantityMapping, session=db.session))
admin.add_view(MyModel(SimilarProductMapping, session=db.session))
admin.add_view(MyModel(Shop, session=db.session))
admin.add_view(MyModel(ProductStock, session=db.session))
admin.add_view(MyModel(ProductStockPinCode, session=db.session))
admin.add_view(MyModel(ProductRate, session=db.session))

admin.add_view(MyModel(City, session=db.session))
admin.add_view(MyModel(Locality, session=db.session))
admin.add_view(MyModel(Address, session=db.session))

admin.add_view(MyModel(Order, session=db.session))
admin.add_view(MyModel(OrderedProduct, session=db.session))
admin.add_view(MyModel(OrderTaxes, session=db.session))
admin.add_view(MyModel(DeliveryBoy, session=db.session))
admin.add_view(MyModel(UserCart, session=db.session))
admin.add_view(MyModel(UserCartItem, session=db.session))

admin.add_view(MyModel(Log, session=db.session))
admin.add_view(MyModel(OfferImage, session=db.session))

path = op.join(op.dirname(__file__))
admin.add_view(FileAdmin(path, '', name='Static Files'))
