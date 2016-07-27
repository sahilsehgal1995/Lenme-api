from datetime import datetime

from flask_security import  current_user
from flask_security.utils import verify_and_update_password, login_user
from flask_security.views import register_user
from flask_security.recoverable import reset_password_token_status, update_password
from sqlalchemy import and_, or_
from sqlalchemy.exc import OperationalError, IntegrityError
from flask import jsonify, request, make_response, redirect

from src import api, OpenResource, db, CustomerResource, AdminResource
from .models import UserProfile, User, Address, Coupon, CouponUserMapping, Role
from .schemas import UserSchema, UserProfileSchema, AddressSchema, CouponSchema


class UserResource(CustomerResource):

    model = User
    schema = UserSchema

    def get(self, slug):
        user = self.model.query
        if current_user.has_roles('customer'):
            user = user.get(current_user.id)
        elif current_user.has_roles:
            user = user.get(slug)
        if not user:
            return make_response(jsonify({'error': 100, 'message': 'User not found'}), 404)
        user_dump = self.schema().dump(user).data
        db.session.commit()

        return jsonify({'success': 200, 'data': user_dump})

    def put(self, slug):

        user = self.model.query.get(slug)
        if not user:
            return make_response(jsonify({'error': 100, 'message': 'User not found'}), 404)
        user, errors = self.schema().load(request.json, instance=user)
        if errors:
            return make_response(jsonify({'error': 101, 'message': str(errors)}), 403)
        db.session.commit()

        return jsonify({'success': 200, 'message': 'user updated successfully', 'data': self.schema().dump(user).data})

    def delete(self, slug):

        is_deleted = self.model.query.delete(slug)
        if not is_deleted:
            return make_response(jsonify({'error': 102, 'message': 'user deletion failed'}))
        db.session.commit()
        return jsonify({'success': 200, 'message': 'user deleted successfully'})


class UserListResource(OpenResource):

    model = User
    schema = UserSchema

    def get(self):
        users = self.model.query
        for key in request.args:
            if hasattr(self.model, key):
                values = request.args.getlist(key)  # one or many
                users = users.filter(getattr(self.model, key).in_(values))
        if 'page' not in request.args:
            resources = users.all()
        else:
            resources = users.paginate(
                int(request.args['page'])).items
        return jsonify({'success': 200, 'data': self.schema().dump(resources, many=True)})

    def post(self):

        # users, errors = self.schema().load(request.json, session=db.session)
        # if errors:
        #     return make_response(jsonify({'error': 101, 'message': str(errors)}), 403)
        try:
            users = register_user(**request.json)
            users.active = True
            users.roles.append(Role.query.filter(Role.name == 'customer').first())
            
            db.session.commit()
        except (OperationalError, IntegrityError) as e:
            db.session.rollback()
            return make_response(jsonify({'error': True, 'data': str(e)}), 403)
        return jsonify({'success': 200, 'message': 'users added successfully'})


api.add_resource(UserListResource, '/users/', endpoint='users')
api.add_resource(UserResource, '/user/<int:slug>/', endpoint='user')


class UserProfileResource(OpenResource):

    model = UserProfile
    schema = UserProfileSchema

    def get(self, slug):

        user_profile = self.model.query.get(slug)
        if not user_profile:
            return make_response(jsonify({'error': 100, 'message': 'User Profile not found'}), 404)
        user_profile_dump = self.schema().dump(user_profile).data
        db.session.commit()

        return jsonify({'success': 200, 'data': user_profile_dump})

    def put(self, slug):

        user_profile = self.model.query.get(slug)
        if not user_profile:
            return make_response(jsonify({'error': 100, 'message': 'User Profile not found'}), 404)
        user_profile, errors = self.schema().load(instance=user_profile)
        if errors:
            return make_response(jsonify({'error': 101, 'message': str(errors)}), 403)
        db.session.commit()

        return jsonify({'success': 200, 'message': 'user_profile updated successfully', 'data': self.schema().dump(user_profile).data})

    def delete(self, slug):

        is_deleted = self.model.query.delete(slug)
        if not is_deleted:
            return make_response(jsonify({'error': 102, 'message': 'user_profile deletion failed'}))
        db.session.commit()
        return jsonify({'success': 200, 'message': 'user_profile deleted successfully'})


class UserProfileListResource(OpenResource):

    model = UserProfile
    schema = UserProfileSchema

    def get(self):
        user_profiles = self.model.query
        for key in request.args:
            if hasattr(self.model, key):
                values = request.args.getlist(key)  # one or many
                user_profiles = user_profiles.filter(getattr(self.model, key).in_(values))
        if 'page' not in request.args:
            resources = user_profiles.all()
        else:
            resources = user_profiles.paginate(
                int(request.args['page'])).items
        return jsonify({'success': 200, 'data': self.schema().dump(resources, many=True)})

    def post(self):

        user_profile, errors = self.schema().load(request.json, session=db.session)
        if errors:
            return make_response(jsonify({'error': 101, 'message': str(errors)}), 403)
        db.session.commit()
        return jsonify({'success': 200, 'message': 'user_profile added successfully', 'data': self.schema().dump(user_profile).data})

api.add_resource(UserProfileResource, '/user_profile/<int:slug>/', endpoint='user_profile')
api.add_resource(UserProfileListResource, '/user_profiles/', endpoint='user_profiles')


class AddressListResource(OpenResource):

    model = Address
    schema = AddressSchema

    def get(self):
        addresses = self.model.query
        for key in request.args:
            if hasattr(self.model, key):
                values = request.args.getlist(key)  # one or many
                addresses = addresses.filter(getattr(self.model, key).in_(values))
        if 'page' not in request.args:
            resources = addresses.all()
        else:
            resources = addresses.paginate(
                int(request.args['page'])).items
        return jsonify({'success': 200, 'data': self.schema().dump(resources, many=True)})

    def post(self):
        if 'id' in request.json and request.json['id']:
            addresses, errors = self.schema().load(request.json, instance=self.model.query.get(request.json['id']))
            if errors:
                return make_response(jsonify({'error': 101, 'message': str(errors)}), 403)

        else:
            addresses, errors = self.schema().load(request.json, session=db.session)
            if errors:
                return make_response(jsonify({'error': 101, 'message': str(errors)}), 403)
            db.session.add(addresses)
        addresses.user_id = request.json['user_id']
        db.session.commit()
        return jsonify({'success': 200, 'message': 'user_profile added successfully', 'data': self.schema().dump(addresses).data})

api.add_resource(AddressListResource, '/addresses/', endpoint='addresses')


class CouponListResource(OpenResource):
    model = Coupon
    schema = CouponSchema

    def get(self):

        coupon = self.model.query.join(CouponUserMapping, and_(CouponUserMapping.coupon_id == Coupon.id))\
            .filter(or_(and_(Coupon.name == request.args['coupon'], Coupon.expiry > datetime.now(),
                             CouponUserMapping.user_id == 1),
                        and_(Coupon.name == request.args['coupon'], Coupon.expiry > datetime.now(), Coupon.for_all == True))).first()
        if coupon:
            return jsonify({'success': 200, 'data': self.schema().dump(coupon).data})
        return make_response((jsonify({'error': 102, 'message': 'Coupon not found'})), 403)

api.add_resource(CouponListResource, '/coupons/', endpoint='coupons')


class UserLoginResource(OpenResource):

    model = User
    schema = UserSchema

    def post(self):

        if request.json:
            data = request.json

            user = self.model.query.filter(self.model.email == data['email']).first()
            print (user)
            if user and verify_and_update_password(data['password'], user) and login_user(user):
                user_data = self.schema().dump(user).data
                return jsonify({'success': 200, 'data': user_data})
            else:
                return make_response(jsonify({'error': 403, 'data': 'invalid data'}), 403)
        else:
            data = request.form
            print(request.form)
            user = self.model.query.filter(self.model.email == data['email']).first()
            if user and verify_and_update_password(data['password'], user) and login_user(user):
                print('sssss')
                return make_response(redirect('/test/v1/admin/', 302))
            else:
                return make_response(redirect('/test/v1/login', 403))
api.add_resource(UserLoginResource, '/login/', endpoint='login')


class UserPasswordResource(OpenResource):

    model = User
    schema = UserSchema

    def post(self):

        if request.json:
            data = request.json

            user = self.model.query.filter(self.model.email == data['email']).first()
            if user:
                from flask_security.recoverable import send_reset_password_instructions
                send_reset_password_instructions(user)
                return jsonify({'success': True})
            return make_response(jsonify({'error': True}), 404)

api.add_resource(UserPasswordResource, '/forgot-password/', endpoint='forgot')


class UserPasswordResetResource(OpenResource):

    def get(self, token):
        expired, invalid, user = reset_password_token_status(token)

        if invalid or expired:
            return make_response(jsonify({'error': True}), 403)

        from flask import render_template
        return make_response(render_template('security/reset_password.html', reset_password_token=token))

    def post(self, token):

        expired, invalid, user = reset_password_token_status(token)

        if invalid or expired:
            return make_response(jsonify({'error': True}), 403)
        if request.form['password'] == request.form['password2']:

            update_password(user, request.form['password'])
        return make_response(redirect('/#/home/Password-Reset-Success'))

api.add_resource(UserPasswordResetResource, '/reset-password/<string:token>/', endpoint='reset')
