from flask_jwt import jwt_required
import json
from flask_restful import Resource,reqparse
from flask import request
from model.userModel import UserModel


class User(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        'username',
        type=str,
        required = True,
        help = 'This field cannot be left blank'
    )
    parser.add_argument(
        'password',
        type=str,
        required = True,
        help = 'This field cannot be left blank'
    )


    def post(self):
        data = User.parser.parse_args()
        username = data['username']
        password = data['password']
        user = UserModel()
        user = user.create_user(username,password)
        return (user)

    '''@UserModel.token_requiredcurrent_user,'''
    def get(self,userid):
        '''if not (current_user['admin'] or current_user['isdoctor']):
            return({"message":"cannot get the specified user"}),401'''
        user = UserModel()
        result = user.get_one('userid',userid)
        return(result),200

    '''@UserModel.token_required'''
    def put(self,userid):
        '''if not (current_user['admin']):
            return({"message":"cannot update patient"}),401'''
        user = UserModel()
        result = user.promote_user_doc(userid)
        return(result),200

    '''@UserModel.token_required'''
    def delete(self,userid):
        '''if not (current_user['admin']):
            return({"message":"cannot delete patient"}),401'''
        user = UserModel()
        result = user.delete_user(userid)
        return(result)
    
class UserLogin(Resource):

    def post(self):
        auth = request.authorization
        user = UserModel()
        result = user.login(auth)
        return(result)

    '''@UserModel.token_required'''
    def put(self,userid):
        '''if not (current_user['admin']):
            return({"message":"cannot update patient"}),401'''
        user = UserModel()
        result = user.promote_user_admin(userid)
        return(result),200

    '''@UserModel.token_requiredcurrent_user,'''
    def delete(self):
        '''if not (current_user['admin']):
            return({"message":"cannot delete patient"}),401'''
        user = UserModel()
        result = user.delete_user_table()
        return(result),200




        