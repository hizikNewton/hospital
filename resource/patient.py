from flask_restful import Api,reqparse
from flask_jwt import jwt_required
import json
from flask_restful import Resource
from model.patientModel import PatientModel
from model.hospitalModel import HospitalModel
from model.userModel import UserModel


class Patient(Resource):

    
    '''@UserModel.token_requiredcurrent_user,'''
    def post(self,hospital_name):
        '''if not current_user['admin']:
            return({"message":"cannot create patient"}),401'''
        parser = reqparse.RequestParser()
        parser.add_argument(
        'name',
        type = str,
        required = True,
        help = '{"name":"Patient Name"}'
        )
        parser.add_argument(
        'surname',
        type = str,
        required = True,
        help = '{"name":"Patient Surname"}'
        )
        parser.add_argument(
            'record',
            required = True,
            help = "patient's Record"
        )
        parser.add_argument(
            'category',
            required = True,
            help = "patient's disease category"
        )
        
        data = parser.parse_args()
        name = data['name']
        surname = data['surname'] 
        record = data['record']
        category = data['category']

        
        patient=PatientModel(hospital_name,surname,name,record)
        patient.category = category
        treatingdoc = patient.get_treating_doctor(patient.category)
        patient.treatingdoc = treatingdoc
        print(treatingdoc)
        patient.insert_patient(category,treatingdoc)
        try:
            return ("New patient {user} created".format(user=name),201)
        except:
            return ("An Error occurred while creating {user}".format(user=name)),400

    
    '''@UserModel.token_requiredcurrent_user,'''
    def get(self,hospital_name,id):
        '''if not (current_user['admin'] or current_user['isdoctor']):
            return({"message":"cannot get patient"}),401'''
        hospital = HospitalModel(hospital_name)
        hosp = hospital.check_hospital_exist(hospital_name)
        if hosp:
            patient = PatientModel(hospital_name)
            patient = patient.get_patient(id,hospital_name)
            return (patient,200)
        else:
            return('{name} Hospital does not exist'.format(name = hospital_name)),404

    
    '''@UserModel.token_requiredcurrent_user,'''
    def put(self,hospital_name,id):
        '''if not( current_user['admin'] or current_user['isdoctor']):
            return({"message":"cannot create update patient record"}),401'''
        patient=PatientModel(hospital_name)
        parser = reqparse.RequestParser()
        parser.add_argument(
            "surname"
        )
        parser.add_argument(
            "name"
        )
        parser.add_argument(
            "record"
        )
        parser.add_argument(
            "category"
        )
        parser.add_argument(
            "imgurl"
        )
        parser.add_argument(
            "biodata"
        )
        data = parser.parse_args()
        updatedict = {
        "patient_surname":data['surname'],
        "patient_name":data['name'],
        "record":data['record'],
        "category":data['category'],
        "imgurl":data['imgurl'],
        "biodata":data['biodata']
        }
        empty = list(filter(lambda i:updatedict[i]==None,updatedict))
        for i in empty:
            updatedict.pop(i)
        update = patient.update_patient_record(id,updatedict)
        return (update),200

    
    '''@UserModel.token_requiredcurrent_user,'''
    def delete(self,hospital_name,id):
        '''if not current_user['admin']:
            return({"message":"cannot delete patient"}),401'''
        patient=PatientModel(hospital_name)
        patRec = patient.delete_patient_rec(id)
        return(patRec),200

class PatientList(Resource):
    
    
    '''@UserModel.token_requiredcurrent_user,'''
    def get(self,hospital_name):
        '''if not (current_user['admin'] or current_user['isdoctor']):
            return({"message":"cannot get the list of patient"}),401'''
        hospital = HospitalModel(hospital_name)
        hosp = hospital.check_hospital_exist(hospital_name)
        if hosp:
            patient = PatientModel(hospital_name,patient_name='',record='')
            patient = patient.get_all_patient(hospital_name)
            return (patient),200
        else:
            return('{name} Hospital does not exist'.format(name = hospital_name)),400
    


class PatientRecord(Resource):

    def put(self,hospital_name,id):
        patient=PatientModel(hospital_name)
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
        
        result = patient.uploadwithPyre(path,privatekey,id)
        if patient.check_id(id):
            try:
                return ({"res":result}),200
            except:
                return("Verify upload path and ensure image exist"),404
        else:
            return({"message":"patient not found"}),404