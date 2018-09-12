from flask import Flask,jsonify,request
from flask_restful import Api,reqparse
from flask_jwt import JWT,jwt_required,jwt

from resource.hospital import Hospital,Hospitals
from resource.patient import Patient,PatientList
from resource.doctor import Doctor,DoctorRecord
from resource.user import User,UserLogin
from resource.record import Record

from model.userModel import UserModel


app = Flask('__name__')
app.config['JAWSDB_URL']= 'mysql://pwpx9lp53pp7oobn:q4f6xa3l2ter9vvk@l3855uft9zao23e2.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/hrnvjd7k86z6nj96'
app.config['secret_key'] = 'OLURIN ANUOLUWAPO'
api = Api(app)
parser = reqparse.RequestParser()


            





api.add_resource(Hospital,'/hospital','/hospital/<string:hospital_name>')
api.add_resource(Hospitals,'/hospitals')

api.add_resource(Patient,'/hospital/<string:hospital_name>/patient','/hospital/<string:hospital_name>/patient/<int:id>')
api.add_resource(PatientList,'/hospital/<string:hospital_name>/patients')

api.add_resource(Doctor,'/hospital/<string:hospital_name>/doctor','/hospital/<string:hospital_name>/doctor/<int:id>')
api.add_resource(DoctorRecord,'/hospital/<string:hospital_name>/doctors','/hospital/<string:hospital_name>/doctor/<int:id>/<string:dbcolumn>')

api.add_resource(Record,'/hospital/<string:hospital_name>/loadcsvrecord')

api.add_resource(User,'/user','/user/<string:userid>','/user/doctor/<string:userid>')
api.add_resource(UserLogin,'/user/login','/users','/user/login/admin/<string:userid>')


if (__name__) == ('__main__'):
    app.run(port=5000,debug=True) 