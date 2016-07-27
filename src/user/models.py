from hashlib import md5

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select, func
from flask_security import RoleMixin, UserMixin
from src import db, BaseMixin, ReprMixin
from src.utils.serializer_helper import serialize_data

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer, db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin, ReprMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, BaseMixin, ReprMixin, UserMixin):

    email = db.Column(db.String(127), unique=True, nullable=False)
    password = db.Column(db.String(255), default='', nullable=False)
    number = db.Column(db.BigInteger)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())

    last_login_ip = db.Column(db.String(45))
    current_login_ip = db.Column(db.String(45))
    login_count = db.Column(db.Integer)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), unique=True)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    user_profile = db.relationship('UserProfile', uselist=False, backref='user')
    addresses = db.relationship('Address', uselist=True, backref='user', lazy='dynamic')
    coupons = db.relationship('CouponUserMapping', back_populates='customer')

    @staticmethod
    def hash_md5(data):
        return md5(data.encode('utf-8')).hexdigest()

    def get_auth_token(self):
        pass

    def generate_auth_token(self):
        token = serialize_data([str(self.id), self.hash_md5(self.password)])
        return token

    @hybrid_property
    def is_admin(self):
        return self.has_role('admin') or self.has_role('shop_owner')

    @hybrid_property
    def is_admin(self):
        return self.has_role('admin') or self.has_role('shop_owner')


    @hybrid_property
    def first_name(self):
        return self.user_profile.first_name or ''

    @hybrid_property
    def last_name(self):
        return self.user_profile.last_name or ''

    @first_name.expression
    def first_name(cls):
        return select([func.lower(UserProfile.first_name)]).where(UserProfile.user_id == cls.id).as_scalar()

    @last_name.expression
    def last_name(cls):
        return select([UserProfile.last_name]).where(UserProfile.user_id == cls.id).as_scalar()

    @hybrid_property
    def authentication_token(self):
        return self.generate_auth_token()


class UserProfile(db.Model, BaseMixin):

    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    # dob = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=True)
    profile_picture = db.Column(db.String(512), nullable=True)
    address = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True)


class Address(db.Model, BaseMixin):

    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255), nullable=True)
    pin_code = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    locality = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(255), nullable=True)
    # locality_id = db.Column(db.Integer, db.ForeignKey('locality.id'))
    #
    # locality = db.relationship('Locality', uselist=False, backref='address')
    #
    # @hybrid_property
    # def locality_name(self):
    #     return self.locality.name
    #
    # @locality_name.expression
    # def locality_name(cls):
    #     return select([Locality.name]).where(Locality.id == cls.locality_id).as_scalar()


class Locality(db.Model, BaseMixin):

    name = db.Column(db.String(127), nullable=False)
    city = db.Column(db.Integer, db.ForeignKey('city.id'))


class City(db.Model, BaseMixin):

    name = db.Column(db.String(55))


class Coupon(db.Model, BaseMixin, ReprMixin):

    name = db.Column(db.String(255))
    discount_type = db.Column(db.Enum('value', 'percentage'), default='percentage')
    discount = db.Column(db.Float(precision=2))
    max_usage = db.Column(db.SmallInteger)
    min_usage = db.Column(db.SmallInteger)
    for_all = db.Column(db.Boolean(True))
    expiry = db.Column(db.DateTime)
    is_taxable = db.Column(db.Boolean(True))
    customers = db.relationship('CouponUserMapping', back_populates='coupon')


class CouponUserMapping(db.Model, BaseMixin):

    id = db.Column(db.Integer, primary_key=True)
    used = db.Column(db.SmallInteger, primary_key=True)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupon.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    customer = db.relationship('User', back_populates='coupons')
    coupon = db.relationship('Coupon', back_populates='customers')

