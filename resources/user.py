from datetime import datetime

from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt,
    get_jwt_identity)
from werkzeug.security import safe_str_cmp
from marshmallow import ValidationError

from blacklist import BLACKLIST
from db import db
from models.user import UserModel

USER_ALREADY_EXISTS = "A user with that username already exists."
USER_EMAIL_EXISTS = "A user with this email already exists."
CREATED_SUCCESSFULLY = "User created successfully."
USER_NOT_FOUND = "User not found."
USER_DELETED = "User deleted."
INVALID_CREDENTIALS = "Invalid credentials!"
USER_UPDATED="User details updated successfully."
USER_LOGGED_OUT = "User <id={user_id}> successfully logged out."

# root_parser = reqparse.RequestParser()
nested_one_parser = reqparse.RequestParser()
details_nested_one_parser = reqparse.RequestParser()
# root_parser.add_argument('params', type=dict, required=True, help='this field cannot be blank')
# root_parser.add_argument('jsonrpc', type=str, required=True, help='this field cannot be blank')
# root_parser.add_argument('method', type=str, required=True, help='this field cannot be blank')
# root_parser.add_argument('id', type=int, required=True, help='this field cannot be blank')


class UserRegister(Resource):
    nested_one_parser.add_argument('username', type=str)
    nested_one_parser.add_argument('password', type=str, required=True,
                                   help="This field cannot be blank.")
    nested_one_parser.add_argument('email', type=str, required=True,
                                   help="This field cannot be blank.")
    nested_one_parser.add_argument('pwResetRequired', type=bool)
    nested_one_parser.add_argument('displayName', type=str)
    nested_one_parser.add_argument('headline', type=str)
    nested_one_parser.add_argument('firstName', type=str)
    nested_one_parser.add_argument('middleInitial', type=str)
    nested_one_parser.add_argument('lastName', type=str)
    nested_one_parser.add_argument('suffix', type=str)
    nested_one_parser.add_argument('phone', type=str)
    nested_one_parser.add_argument('address1', type=str)
    nested_one_parser.add_argument('address2', type=str)
    nested_one_parser.add_argument('city', type=str)
    nested_one_parser.add_argument('state', type=str)
    nested_one_parser.add_argument('zip', type=int)
    nested_one_parser.add_argument('birthDate', type=lambda x: datetime.strptime(x, '%B %d, %Y'))

    def post(self):
        try:
            # root_args = root_parser.parse_args()
            nested_one_args = nested_one_parser.parse_args()

        except ValidationError as err:
            return err.messages, 400

        if UserModel.find_by_username(nested_one_args['username']):
            return {"message": USER_ALREADY_EXISTS}, 400

        if UserModel.find_by_email(nested_one_args['email']):
            return {"message": USER_EMAIL_EXISTS}, 400

        user = UserModel(**nested_one_args)
        user.save_to_db()

        return user.json_data(), 201

class User(Resource):
    details_nested_one_parser.add_argument('userid', type=str, required=True, help="userid is required")


    @classmethod
    #@jwt_required(fresh=True)
    def get(cls):
        details_nested_one_args = details_nested_one_parser.parse_args()
        user = UserModel.find_by_id(details_nested_one_args['userid'])
        if not user:
            return {"message": USER_NOT_FOUND}, 404

        return user.json(), 200

    @classmethod
    @jwt_required(fresh=True)
    def delete(cls):
        details_nested_one_args = details_nested_one_parser.parse_args()
        user = UserModel.find_by_id(details_nested_one_args['userid'])
        if not user:
            return {"message": USER_NOT_FOUND}, 404

        user.delete_from_db()
        return {"message": USER_DELETED}, 200
    
    @classmethod
    #@jwt_required(fresh=True)
    def put(cls):
        details_nested_one_args = details_nested_one_parser.parse_args()
        print('------------')
        print(details_nested_one_args)
        user = UserModel.find_by_id(details_nested_one_args['userid'])
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        user.update_user()
        return {"message": USER_UPDATED}, 204


class UserLogin(Resource):

    @classmethod
    def post(cls):
        # get data from parser
        # root_args = root_parser.parse_args()
        nested_one_args = nested_one_parser.parse_args()
        # find user in database
        user = UserModel.find_by_email(nested_one_args['email'])
        # check password
        if user:
            if safe_str_cmp(user.password, nested_one_args['password']):
                access_token = create_access_token(identity=user.userid, fresh=True)
                refresh_token = create_refresh_token(user.userid)
                return user.loginData(access_token, refresh_token), 200
            else:
                return {'message': 'Password does not match'}, 401
        return {'message': 'No user with this mail id'}, 400


class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLACKLIST.add(jti)
        return {'message': 'successfully logged out'}, 200


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
