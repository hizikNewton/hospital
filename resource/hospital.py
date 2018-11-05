from flask_restful import Api,reqparse
from flask_jwt import jwt_required
import json
from flask_restful import Resource


from model.hospitalModel import HospitalModel
from model.userModel import UserModel

class Hospital(Resource):

    '''@UserModel.token_required'''
    def post(self):
        '''if not current_user['admin']:
            return({"message":"cannot create hospital"}),401'''
        parser = reqparse.RequestParser()
        parser.add_argument(
        'hospital_name',
        type = str,
        required = True,
        help = 'Name of hospital is required'
        )
        data = parser.parse_args()
        hospital_name = data['hospital_name']
        hospital = HospitalModel(hospital_name)
        result = hospital.create_hospital(hospital_name)
        new_hospital= {
            'name':hospital_name,
            'message':result
        }
        return (new_hospital),201


    '''@UserModel.token_requiredcurrent_user,'''
    def get(self,hospital_name):
        '''if not current_user['admin']:
            return({"message":"cannot get hospital"}),401'''

        myhospital = HospitalModel(hospital_name)
        result = myhospital.check_hospital_exist(hospital_name)
        if result:
            myhospital = myhospital.get_hospital(hospital_name)
            return (myhospital),200
        return ('cannot get {name}'.format(name = hospital_name)),404

    '''@UserModel.token_requiredcurrent_user,'''
    def put(self,hospital_name):
        '''if not current_user['admin']:
            return({"message":"cannot update hospital"}),401'''
        parser = reqparse.RequestParser()
        parser.add_argument(
        'hospital_name',
        type = str,
        required = True,
        help = 'Name of hospital to update is required'
        )
        data = parser.parse_args()
        new_name = data['hospital_name']
        myhospital = HospitalModel(hospital_name)
        check = myhospital.check_hospital_exist(hospital_name)
        if check:
            result = myhospital.update_hospital(new_name)
            return (result),200
        else:
            return ({"message":"Hospital does not exist"}),404


    
    '''@UserModel.token_requiredcurrent_user,'''
    def delete(self,hospital_name):
        '''if not current_user['admin']:
            return({"message":"cannot delete hospital"}),401'''
        myhospital = HospitalModel(hospital_name)
        delete = myhospital.delete_hospital()
        return (delete),200


class Hospitals(Resource):
    '''@UserModel.token_required current_user,'''
    def get(self):
        '''if not current_user['admin']:
            return({"message":"cannot get list of hospital"}),401'''
        myhospital = HospitalModel()
        hospitals = myhospital.get_all_hospital()
        return({'list of all hospitals':hospitals}),200




