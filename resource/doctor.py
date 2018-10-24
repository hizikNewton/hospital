from flask_restful import Api,reqparse
from flask_jwt import jwt_required
import json
from flask_restful import Resource
from model.doctorModel import DoctorModel
from model.userModel import UserModel
from flask_cors import cross_origin



class Doctor(Resource):
    
    @UserModel.token_required
    def post(current_user,self,hospital_name):
        if not current_user['admin']:
            return({"message":"cannot create hospital"}),401
        parser = reqparse.RequestParser()
        parser.add_argument(
        'name',
        type = str,
        required = True,
        help = "doctor's name is required"
        )
        parser.add_argument(
        'surname',
        type = str,
        required = True,
        help = "doctor's surname is required"
        )
        parser.add_argument(
            'biodata',
            required = True,
            help ="doctor's biodata record is required"
        )
        parser.add_argument(
            'specialization',
            required = True,
            help = "Doctor's area of specialization"
        )
        data = parser.parse_args()
        doctor_name = data['name']
        doctor_surname = data['surname']
        biodata = data['biodata']
        spec = data['specialization']
        doctor=DoctorModel(hospital_name,doctor_surname,doctor_name,spec,biodata)
        try:
            doctor.insert_doctor()
        except:
            return ("An Error occurred while creating {user}".format(user=doctor_name)),404
        return "Doctor created",201

    
    '''@UserModel.token_required current_user,'''
    def get(self,hospital_name,id):
        '''if not (current_user['isdoctor'] or current_user['admin']):
            return({"message":"cannot create hospital"}),401'''
        doctor=DoctorModel(hospital_name)
        data = doctor.get_doctor_record(id,hospital_name)
        return(data),200

    
    '''@UserModel.token_requiredcurrent_user,'''
    def put(self,hospital_name,id):
        '''if not (current_user['isdoctor'] or current_user['admin']):
            return({"message":"cannot update doctor"}),401'''

        doctor=DoctorModel(hospital_name)
        parser = reqparse.RequestParser()
        parser.add_argument(
            "name"
        )
        parser.add_argument(
            "specialization"
        )
        parser.add_argument(
            "biodata"
        )
        data = parser.parse_args()
        updatedict = {"doctor_name":data['name'],
        "specialization":data['specialization'],
        "biodata":data['biodata']
        }
        empty = list(filter(lambda i:updatedict[i]==None,updatedict))
        for i in empty:
            updatedict.pop(i)
        try:
            update = doctor.update_doctor_record(id,updatedict)
            return (update),200
        except:
            return({"message":"cannot update doctor's record"}),404

    
    '''@UserModel.token_requiredcurrent_user,'''
    def delete(self,hospital_name,id):
        '''if not (current_user['isdoctor'] or current_user['admin']):
            return({"message":"cannot delete doctor"}),401'''
        doctor=DoctorModel(hospital_name)
        try:
            delRec = doctor.delete_doctor_rec(id)
            return(delRec)
        except:
            return({"message":"Id does not exist"}),404



class DoctorRecord(Resource):
    doctorField = ['doctor_name','specialization','biodata']
    '''@UserModel.token_requiredcurrent_user,'''
    def post(self,hospital_name):
        '''if not (current_user['isdoctor'] ):
            return({"message":"cannot create list of doctors"}),401'''
        doctor=DoctorModel(hospital_name)
        parser = reqparse.RequestParser()
        parser.add_argument(
            "path",
            required = True,
            help = "include a path,path should be specified:path\\to\\file"
        )
        data = parser.parse_args()
        path = data['path']
        try:
            result = doctor.create_many_doctors(path)
            return(result),200
        except:
            return("Error ocurred while creating list of doctors"),500
            


        
    '''@UserModel.token_required current_user,'''
    
    @cross_origin(headers=['Content-Type'])
    def get(self,hospital_name,id,dbcolumn):
        '''if not (current_user['isdoctor'] or current_user['admin']):
            return({"message":"cannot create hospital"}),401'''
        doctor=DoctorModel(hospital_name)
        if dbcolumn in DoctorRecord.doctorField:
            data = doctor.get_doctor_record(id,hospital_name,dbcolumn=dbcolumn)
            return(data),200
        else:
            return({"message":"You can only request one of doctor_name,specialization,biodata"}),404



    @UserModel.token_required
    def put(current_user,self,hospital_name):
        if not (current_user['isdoctor'] or current_user['admin']):
            return({"message":"cannot create hospital"}),401
        doctor=DoctorModel(hospital_name)
        parser = reqparse.RequestParser()
        parser.add_argument(
        "path",
        type = str,
        required = True,
        help = "image path must should be specified:path\\to\\file"
        )
        parser.add_argument(
        "privatekey",
        type = str,
        required = True,
        help = "doctors must have my private key"
        )
        data = parser.parse_args()
        path = data['path']
        privatekey = data['privatekey']
        
        
        try:
            doctor.uploadwithPyre(path,privatekey,current_user)
            return ("successful"),200
        except:
            return("Verify upload path and ensure image exist"),404

