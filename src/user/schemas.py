from src import ma, BaseSchema
from .models import UserProfile, User, Address, Coupon


class UserSchema(BaseSchema):

    class Meta:
        model = User
        exclude = ('created_on', 'updated_on', 'password', 'roles', 'confirmed_at',
                   'last_login_ip', 'last_login_at', 'current_login_at', 'current_login_ip')

    id = ma.Integer(dump_only=True)
    email = ma.Email()
    name = ma.String()
    user_profile = ma.Nested('UserProfileSchema', many=False)
    authentication_token = ma.String()
    roles = ma.List(ma.String)
    first_name = ma.String()
    last_name = ma.String()
    is_admin = ma.Boolean()
    addresses = ma.Nested('AddressSchema', many=True)


class UserProfileSchema(BaseSchema):

    class Meta:
        model = UserProfile
        exclude = ('created_on', 'updated_on', 'user', 'dob')

    id = ma.Integer(dump_only=True)


class AddressSchema(BaseSchema):

    class Meta:
        model = Address
        exclude = ('created_on', 'updated_on')

        id = ma.Integer(load=True)
        user_id = ma.Integer(load=True)


class CouponSchema(BaseSchema):

    class Meta:
        model = Coupon
        exclude = ('created_on', 'updated_on', 'customers')

    id = ma.Integer(dump_only=True)
    coupon_code = ma.String()
    discount = ma.Float()
