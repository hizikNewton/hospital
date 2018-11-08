import os
from flask import Flask,jsonify,request
from flask_restful import Api,reqparse
from flask_jwt import JWT,jwt_required,jwt
from flask_cors import CORS

from resource.hospital import Hospital,Hospitals
from resource.patient import Patient,PatientList
from resource.doctor import Doctor,DoctorRecord,Doctors
from resource.user import User,Users
from resource.record import Record


from model.userModel import UserModel


app = Flask('__name__',instance_relative_config=True)
CORS(app, resources = r'/*',headers = 'Content-Type')


app.config['JAWSDB_URL']='mysql://v98vj2rnkd8xjsbn:juvam2griraafgz2@er7lx9km02rjyf3n.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/ec40ra1bb5ef3pkr'

app.config['secret_key'] = 'OLURIN ANUOLUWAPO'

api = Api(app)
parser = reqparse.RequestParser()


            






api.add_resource(Patient,'/hospital/<string:hospital_name>/patient','/hospital/<string:hospital_name>/patient/<int:id>')
api.add_resource(PatientList,'/hospital/<string:hospital_name>/patients')

api.add_resource(Doctor,'/hospital/<string:hospital_name>/doctor','/hospital/<string:hospital_name>/doctor/<string:userid>')

api.add_resource(Doctors,'/hospitals/doctors')

api.add_resource(DoctorRecord,'/hospital/<string:hospital_name>/doctors','/hospital/<string:hospital_name>/doctor/<int:id>/<string:dbcolumn>','/hospital/<string:hospital_name>/doctor/upload')

api.add_resource(Record,'/hospital/<string:hospital_name>/loadcsvrecord')

api.add_resource(User,'/user','/user/<string:userid>','/user/doctor/<string:hospital_name>/<string:userid>')
api.add_resource(Users,'/user/login','/users','/user/admin/<string:userid>')

api.add_resource(Hospital,'/hospital','/hospital/<string:hospital_name>')
api.add_resource(Hospitals,'/hospitals')

if (__name__) == ('__main__'):
    app.run(port=5000,debug=False) 