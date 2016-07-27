from src import ma, BaseSchema
from marshmallow import post_dump, pre_dump

from .models import Category, Product, Taxes, Rating, Description, Brand, \
    SpecificDetails, CustomerQuestion, CustomerAnswer, PinCode, ProductRate, ProductStock, ProductImage, ProductQuantityMapping,\
    SimilarProductMapping, Shop, ProductStockPinCode, OfferImage


class CategorySchema(BaseSchema):

    class Meta:
        model = Category
        exclude = ('created_on', 'updated_on')
    id = ma.Integer(load=True)
    name = ma.String()
    parent = ma.Nested('self', exclude=('products', 'children', 'parent'), default=None, dump_only=True)
    children = ma.Nested('self', exclude=('products',), default=None, many=True, dump_only=True)
    parent_id = ma.Integer(load_only=True, dump=False, allow_none=True)


class ProductRateSchema(BaseSchema):
    class Meta:
        model = ProductRate
        exclude = ('created_on', 'updated_on', 'product_id', 'product')


class ProductSchema(BaseSchema):

    class Meta:
        model = Product
        exclude = ('created_on', 'updated_on', 'product_availability')

    id = ma.Integer(load=True)
    name = ma.String()
    brand_id = ma.Integer(load_only=True)
    # brand = ma.Nested('BrandSchema', only=('name',), many=False, dump_only=True)
    brand_name = ma.String()
    price = ma.Integer()
    discount = ma.Float()
    taxes = ma.Nested('TaxesSchema', many=True, dump_only=True)
    base_category = ma.String()
    category_name = ma.String()
    all_categories = ma.List(ma.String)
    category_id = ma.Integer(load=True, dump=False)
    category = ma.Nested('CategorySchema', exclude=('products', 'children'), many=False, dump_only=True)
    parent_category = ma.String()
    is_bulk_discounted = ma.Boolean()
    grand_parent_category = ma.String()
    local_mrp = ma.Float(precision=2)
    mrp = ma.Float(precision=2)
    images = ma.Nested('ProductImageSchema', many=True, dump_only=True)
    description = ma.Nested('DescriptionSchema', many=False, dump_only=True)
    similar_quantity_products = ma.Nested('ProductQuantityMappingSchema', many=True, dump_only=True)
    rates = ma.Nested('ProductRateSchema', many=True, dump_only=True)
    product_stocks = ma.Nested('ProductStockSchema', exclude=('pin_code',), many=True, dump_only=True)


class TaxesSchema(BaseSchema):

    class Meta:
        model = Taxes
        exclude = ('created_on', 'updated_on', 'products')

    id = ma.Integer(load=True)
    tax_type = ma.String()
    tax_percentage = ma.Float()
    is_cascading = ma.Boolean()


class RatingSchema(BaseSchema):

    class Meta:
        model = Rating

    id = ma.Integer(dump_only=True)
    product_id = ma.Nested('ProductSchema')
    user_id = ma.Nested('UserSchema')
    rating = ma.String()


class DescriptionSchema(BaseSchema):

    class Meta:
        model = Description
        exclude = ('created_on', 'updated_on', 'products')

    id = ma.Integer(dump_only=True)
    description = ma.String()
    product_id = ma.Integer(load_only=True)


class ProductQuantityMappingSchema(BaseSchema):

    class Meta:
        model = ProductQuantityMapping
        exclude = ('created_on', 'updated_on')

    id = ma.Integer(load=True)
    quantity = ma.Nested('ProductSchema', only=('quantity', 'id', 'rates', 'price', 'taxes', 'name', 'market_price', 'mrp'))
    quantity_product_id = ma.Integer(load_only=True)
    product_id = ma.Integer(load_only=True)


class SimilarProductMappingSchema(BaseSchema):

    class Meta:
        model = SimilarProductMapping
        exclude = ('created_on', 'updated_on')

    id = ma.Integer(load=True)
    similar_product = ma.Nested('ProductSchema', dump_only=True)
    similar_product_id = ma.Integer(load_only=True)
    product_id = ma.Integer(load_only=True)


class ProductImageSchema(BaseSchema):

    class Meta:
        model = ProductImage
        exclude = ('created_on', 'updated_on', 'products')

    id = ma.Integer(load=True)
    image = ma.String()
    product_id = ma.Integer(load=True)


class SpecificDetailsSchema(BaseSchema):

    class Meta:
        model = SpecificDetails

    id = ma.Integer(dump_only=True)
    details = ma.String()
    documentation = ma.String()
    warranty = ma.Integer()
    product_id = ma.Nested('ProductSchema', many=False)


class BrandSchema(BaseSchema):

    class Meta:
        model = Brand
        exclude = ('created_on', 'updated_on', 'products')

    id = ma.Integer(dump_only=True)


class CustomerQuestionSchema(BaseSchema):

    class Meta:
        model = CustomerQuestion

    id = ma.Integer(dump_only=True)
    question = ma.String()
    votes = ma.Integer()
    answer_count = ma.Integer()
    user_id = ma.Nested('UserSchema', many=False)


class CustomerAnswerSchema(BaseSchema):

    class Meta:
        model = CustomerAnswer

    id = ma.Integer(dump_only=True)
    answer = ma.String()
    user_id = ma.Nested('UserSchema', many=False)
    question_id = ma.Nested('CustomerQuestionSchema', many=False)


class PinCodeSchema(BaseSchema):

    class Meta:
        model = PinCode

    id = ma.Integer(dump_only=True)
    pin_code = ma.Integer()


class ProductStockSchema(BaseSchema):

    class Meta:
        model = ProductStock
        exclude = ('created_on', 'updated_on', 'pin_codes')

    id = ma.Integer(dump_only=True)
    delivery_charge = ma.Float()
    delivery_time = ma.Integer()
    product_id = ma.Integer(load=True)
    product = ma.Nested('ProductSchema', only=('id', 'name', 'category', 'price'), dump_only=True)
    stock = ma.Integer()
    pin_code_list = ma.List(ma.Integer)
    shop = ma.Nested('ShopSchema', many=False, dump_only=True)
    shop_id = ma.Integer(load=True)


class ShopSchema(BaseSchema):

    class Meta:
        model = Shop
        exclude = ('created_on', 'updated_on', 'shop_stocks')
        fields = ('id', 'total_products', 'total_stock', 'owner_name', 'address', 'locality', 'city', 'pin_code', 'name')

        id = ma.Integer(load=True)
        total_products = ma.String()
        total_stock = ma.String()
        owner_name = ma.String()


class ProductStockPinCodeSchema(BaseSchema):

    class Meta:
        model = ProductStockPinCode
        exclude = ('created_on', 'updated_on')

        id = ma.Integer(load=True)
        product_stock_id = ma.Integer(load=True)
        pin_code_id = ma.Integer(load=True)


class OfferImageSchema(BaseSchema):

    class Meta:
        model = OfferImage
        exclude = ('created_on', 'updated_on')

        id = ma.Integer(load=True)

