
from flask_restful import Api,reqparse
from flask_jwt import jwt_required
import json
from flask_restful import Resource
from flask_cors import cross_origin
import dill
import pandas as pd
import os
from model.patientModel import PatientModel

class Predict(Resource):
    
    def post(self,hospital_name,id):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'Gender',
            type = str,
            required = True,
            help = "Gender is required and type is of string"
        )
        parser.add_argument(
            'Control',
            type = int,
            required = True,
            help = "Control is required and type is of integer"
        )
        parser.add_argument(
            'AST',
            type = int,
            required = True,
            help ="AST record is required and type is of integer"
        )
        parser.add_argument(
            'WBC',
            type = int,
            required = True,
            help ="WBC record is required and type is of integer"
        )
        parser.add_argument(
            'HBVDNA',
            type = int,
            required = True,
            help ="HBVDNA is required and type is of integer"
        )
        parser.add_argument(
            'HBeAg',
            type = str,
            required = True,
            help ="HBeAg is required  and type is of string"
        )
        parser.add_argument(
            'lymph',
            type = int,
            required = True,
            help = "lymph is required and type is of integer"
        )

        data = parser.parse_args()

        Gender = data['Gender']
        
        Control = data['Control']
        
        AST = data['AST']
        
        WBC = data['WBC']
        
        HBeAg = data['HBeAg']
        
        HBVDNA = data['HBVDNA']
        
        lymph = data['lymph']

        basedir = os.getcwd()
        basedir = os.path.realpath(basedir)
        path = os.path.join(basedir,'model2.pkl')
        with open(path,'rb') as f:
            loaded_model=dill.load(f)

        my_data=pd.DataFrame({'GENDER':[Gender],'control':[Control],'AST':[AST],'WBC':[WBC],'HBVDNA':[HBVDNA],'HBeAg':[HBeAg],'lymph':[lymph]})

        predictedval = loaded_model.predict(my_data)

        patient = PatientModel(hospital_name)

        
        '''updatedict = {
        "biodata":f"(status:{predictedval})"           
            }
        
        patient.update_patient_record(id,updatedict)'''
        
        for item in predictedval:
            if item == 0:
                return({'status':'Low Risk'}),200
            else:
                return({'status':'High Risk'}),200
