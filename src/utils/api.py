from functools import wraps
from flask_restful import Resource, Api
from flask_security import auth_token_required, roles_accepted

from .blue_prints import bp

api = Api(bp)


def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


class AdminResource(Resource):
    method_decorators = [roles_accepted('admin', 'shop_owner'), auth_token_required]


class CustomerResource(Resource):
    method_decorators = [roles_accepted('admin', 'shop_owner', 'customer', 'delivery_boy'), auth_token_required]


class OpenResource(Resource):
    pass
