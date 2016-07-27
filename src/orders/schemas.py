from src import ma, BaseSchema
from .models import Order, OrderedProduct, OrderTaxes, SavedCard, Status, OrderLog, GiftCard, DeliveryBoy, UserCart, UserCartItem
from src.user.schemas import UserSchema, AddressSchema


class OrderSchema(BaseSchema):

    class Meta:
        model = Order

    id = ma.Integer(dump_only=True)
    user_id = ma.Integer(load=True)
    coupon_id = ma.Integer(load=True)
    user = ma.Nested(UserSchema, dump_only=True, many=False)
    address_id = ma.Integer(load=True)
    address = ma.Nested(AddressSchema, dump_only=True, many=False)
    total = ma.Float(precion=2)
    delivery_boy_id = ma.Integer(load=True)
    delivery_boy = ma.Nested('DeliveryBoySchema', many=False, load=False)
    ordered_product = ma.Nested('OrderedProductSchema', many=True)


class OrderedProductSchema(BaseSchema):

    class Meta:
        model = OrderedProduct
        exclude = ('created_on', 'updated_on', 'order')

    id = ma.Integer(dump_only=True)
    quantity = ma.Integer()
    price = ma.Float()
    discount = ma.Float()
    product = ma.Nested('ProductSchema', only=('name',), many=False)
    coupon = ma.Nested('CouponSchema', many=False)
    product_id = ma.Integer(load=True)
    coupon_id = ma.Integer(load=True)
    order_id = ma.Integer(load=True)
    shop_id = ma.Integer(load=True, dump=True)
    shop = ma.Nested('ShopSchema', only=('id', 'name'), many=False)


class OrderTaxesSchema(BaseSchema):

    class Meta:
        model = OrderTaxes

    tax_amount = ma.Float()
    taxable_amount = ma.Float()
    order_product = ma.Nested('OrderedProductSchema', many=False, load=False)
    tax = ma.Nested('TaxesSchema', many=False, load=False)
    order_product_id = ma.Integer(load_only=True)
    tax_id = ma.Integer(load_only=True)


class SavedCardSchema(BaseSchema):

    class Meta:
        model = SavedCard

    id = ma.Integer(dump_only=True)
    card_number = ma.Integer()
    card_holder_name = ma.String()
    card_expiry_date = ma.DateTime()
    user_id = ma.Nested('UserSchema', many=True)


class StatusSchema(BaseSchema):

    class Meta:
        model = Status

    id = ma.Integer(dump_only=True)
    message = ma.String()
    order_id = ma.Nested('OrderSchema', many=True)


class OrderLogSchema(BaseSchema):

    class Meta:
        model = OrderLog

    id = ma.Integer(dump_only=True)
    order_status = ma.String()
    order_id = ma.Nested('OrderSchema')


class GiftCardSchema(BaseSchema):

    class Meta:
        model = GiftCard

    id = ma.Integer(dump_only=True)
    value = ma.Integer()
    receiver_email = ma.String()
    to_name = ma.String()
    from_name = ma.String()
    message = ma.String()
    user_id = ma.Nested('UserSchema')


class DeliveryBoySchema(BaseSchema):
    class Meta:
        model = DeliveryBoy
        exclude = ('created_on', 'updated_on', 'order')

        id = ma.Integer(load=True)


class UserCartSchema(BaseSchema):
    class Meta:
        model = UserCart

    id = ma.Integer(load=True)
    user_id = ma.Integer(load=True)
    user_cart_items = ma.Nested('UserCartItemSchema', many=True)
    user = ma.Nested(UserSchema)


class UserCartItemSchema(BaseSchema):
    class Meta:
        model = UserCartItem

    id = ma.Integer(load=True)
    product_id = ma.Integer(load=True)
    user_cart_id = ma.Integer(load=True)
    product = ma.Nested('ProductSchema')