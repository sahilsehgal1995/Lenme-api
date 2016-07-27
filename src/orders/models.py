from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select
from sqlalchemy import UniqueConstraint

from src import db, BaseMixin
from src.user.models import User


class DeliveryBoy(db.Model, BaseMixin):
    name = db.Column(db.String(125), nullable=False)
    number = db.Column(db.Integer)
    secret_code = db.Column(db.SmallInteger)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)

    user = db.relationship('User', backref='delivery_boy', uselist=False)
    orders = db.relationship('Order', uselist=True)


class UserCart(db.Model, BaseMixin):
    number = db.Column(db.BigInteger)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', foreign_keys=[user_id])
    user_cart_items = db.relationship('UserCartItem', uselist=True, backref='user_cart', lazy='dynamic', cascade='all, delete, delete-orphan')


class UserCartItem(db.Model, BaseMixin):

    user_cart_id = db.Column(db.Integer, db.ForeignKey('user_cart.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))

    product = db.relationship('Product', uselist=False)

    UniqueConstraint('user_cart_id', 'product_id', name='uix_1')


class Order(db.Model, BaseMixin):

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    address_id = db.Column(db.Integer, db.ForeignKey('address.id', ondelete='CASCADE'))
    sub_total = db.Column(db.Float(precision=2))
    total = db.Column(db.Float(precision=2))
    status = db.Column(db.String(25), nullable=True, default='processing')
    delivery_charge = db.Column(db.Integer)
    discount = db.Column(db.Float(precision=2), default=0)
    otp = db.Column(db.SmallInteger, default=0)
    convenience_charge = db.Column(db.SmallInteger, default=0)
    delivery_instructions = db.Column(db.String(255))

    delivery_boy_id = db.Column(db.Integer, db.ForeignKey('delivery_boy.id'))
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupon.id', ondelete='CASCADE'))

    delivery_boy = db.relationship('DeliveryBoy', foreign_keys=[delivery_boy_id], uselist=False)
    address = db.relationship('Address', foreign_keys=[address_id], uselist=False)
    user = db.relationship('User', foreign_keys=[user_id], uselist=False)
    ordered_product = db.relationship('OrderedProduct', uselist=True, backref='order', lazy='dynamic')

    @hybrid_property
    def customer_name(self):
        return self.user.first_name

    @customer_name.expression
    def customer_name(cls):
        return select([User.first_name]).where(cls.user_id == User.id).as_scalar()

    @hybrid_property
    def customer_number(self):
        return self.user.number

    @customer_number.expression
    def customer_number(cls):
        return select([User.number]).where(cls.user_id == User.id).as_scalar()


class OrderedProduct(db.Model, BaseMixin):

    quantity = db.Column(db.Integer)
    price = db.Column(db.Float(precision=2))
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete='CASCADE'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'))
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id', ondelete='CASCADE'))

    product = db.relationship('Product')
    shop = db.relationship('Shop', backref='ordered_product')


class OrderTaxes(db.Model, BaseMixin):

    order_product_id = db.Column(db.Integer, db.ForeignKey('ordered_product.id', ondelete='CASCADE'))
    tax_id = db.Column(db.Integer, db.ForeignKey('taxes.id', ondelete='CASCADE'))
    tax_amount = db.Column(db.Float(precision=2))
    taxable_amount = db.Column(db.Float(precision=2))


class SavedCard(db.Model, BaseMixin):

    card_number = db.Column(db.Integer)
    card_holder_name = db.Column(db.String(127))
    card_expiry_date = db.Column(db.DateTime())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True)


class Status(db.Model, BaseMixin):

    message = db.Column(db.String(255))
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete='CASCADE'), unique=True)


class OrderLog(db.Model, BaseMixin):

    order_status = db.Column(db.Text())
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete='CASCADE'), unique=True)


class GiftCard(db.Model, BaseMixin):

    value = db.Column(db.Integer)
    receiver_email = db.Column(db.String(255))
    to_name = db.Column(db.String(255))
    from_name = db.Column(db.String(255))
    message = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True)
