import pymysql
import datetime
from .userModel import UserModel
import uuid
import os
import json
from werkzeug.security import generate_password_hash
from firebase import firebase
from google.cloud import storage
from google.cloud.storage import client
import firebase_admin
import pyrebase
from firebase_admin import credentials,storage,auth

connection = pymysql.connect(host ='er7lx9km02rjyf3n.cbetxkdyhwsb.us-east-1.rds.amazonaws.com',user= 'v98vj2rnkd8xjsbn',port = 3306,password = 'juvam2griraafgz2',database = 'ec40ra1bb5ef3pkr')


from mycred import cred
class DoctorModel:
    
    def __init__(self,hospital_name='',doctor_surname='',doctor_name='',spec='',biodata=''):
        self.doctor_name = doctor_name
        self.doctor_surname = doctor_surname
        self.hospital_name = hospital_name.lower()
        self.spec = spec.lower()
        self.biodata = biodata.lower()
        self.table = '{name}_doctors'.format(name=hospital_name)
        self.user = UserModel()
        self.timestamp = datetime.datetime.now().isoformat(timespec='seconds')


    def json(self,*args):
        return {
        "hospital":self.hospital_name,
        "id":args[0],
        "doctor_userid":args[1],
        "doctor_surname":args[2],
        "doctor_name":args[3],
        "specialization":args[4],
        "imgurl":args[5],
        "biodata":args[6]
        }

#create a doctor and a user at the sametime 
    def insert_doctor(self):
        with connection.cursor() as cursor:
            
            table = self.table
            name = self.doctor_name
            surname = self.doctor_surname
            spec = self.spec
            biodata = self.biodata
            timestamp = self.timestamp.replace('T',' ')
            doctor_userid = str(uuid.uuid4())[0:8]
            username = name
            imgurl = ''
            password = generate_password_hash(surname)
            self.user.insert_user(doctor_userid,username,password,timestamp)
            query = f"INSERT INTO {table} (doctor_userid,doctor_name,doctor_surname,specialization,imgurl,biodata,timestamp)VALUES({repr(doctor_userid)},{repr(name)},{repr(surname)},{repr(spec)},{repr(imgurl)},{repr(biodata)},{repr(timestamp)})"
            cursor.execute(query)
            connection.commit()
        
#create list of doctors 
    def create_many_doctors(self,path):
        table_name = self.table
        path = path
        with connection.cursor() as cursor:
            query = f'''LOAD DATA INFILE {repr(path)} INTO TABLE {table_name} COLUMNS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY "\n" '''
            cursor.execute(query)
            connection.commit()

    def get_doctor_record(self,userid,hospital_name,dbcolumn='*'):
        if (self.check_('doctor_userid',userid)):
            with connection.cursor() as cursor:
                name = self.hospital_name
                userid = userid
                dbcolumn=dbcolumn
                query=(f'SELECT {dbcolumn} FROM {name}_doctors WHERE doctor_userid={repr(userid)}')
                cursor.execute(query)
                try:
                    cursor.execute(query)
                except:
                    return ('cannot get requested doctor data')
                else:
                    cursor.execute(query)
                    result = cursor.fetchone()
                    if len(result)>1:
                        return self.json(*result)
                    else:
                        return ({f"{dbcolumn}":result[0]})
                
        else:
            return ("id not found"),404


    def check_id(self,userid,dbcol):
        table = self.table
        with connection.cursor() as cursor:
            query = (f'SELECT dbcol from {table}')
            cursor.execute(query)
            result = []
            res = cursor.fetchone()
            for i in res:
                result.append(i[0])
            if (id in result):
                return(True)
            else:
                return(False)
                
    def check_(self,dbtable_col,value_to_check):
        table_col = dbtable_col
        value = value_to_check
        table = self.table
        with connection.cursor() as cursor:
            query = (f'SELECT {table_col} from {table}')
            cursor.execute(query)
            res = cursor.fetchall()
            result = []
            for i in res:
                result.append(i[0])
            if (value in result):
                return(True)
            else:
                return(False)




    def update_doctor_record(self,userid,updatedict):
        if (self.check_('doctor_userid',userid)):
            with connection.cursor() as cursor:
                cursor.execute('SHOW COLUMNS FROM {table}'.format(table = self.table))
                dbcolumn = cursor.fetchall()
                dbcolumn = list(map(lambda x:x[0],dbcolumn))
                updatekeys = [(item) for item in updatedict for col in dbcolumn if item == col]
                
                querylist = []
                for _key in updatekeys:
                    updateitem = updatedict[_key]
                    table=self.table
                    key = _key
                    updateitem = updateitem
                    query = f"UPDATE {table} SET {key} = {repr(updateitem)} WHERE {table}.doctor_userid={repr(userid)}"
                    querylist.append(query)
                    
                for item in querylist:
                        try:
                            cursor.execute(item)
                            connection.commit()
                        except:
                            return("Unable to update record")
                        
                return("Record updated successfully")
        else:
            return ("id not found"),404


    def delete_doctor_rec(self,userid):
        if (self.check_('doctor_userid',userid)):
            table = self.table
            with connection.cursor() as cursor:
                query = (f"DELETE FROM {table} WHERE {table}.doctor_userid = {userid}")
                cursor.execute(query)
                connection.commit()
                return("Record deleted successfully")
        else:
            return("id not found"),404


     

    def uploadwithPyre(self,filepath,secretkey,current_user):
        table = self.table
        filename_user = current_user["username"]
        cred['private_key'] = secretkey
        userid = current_user["userid"]
        
        config = {
        "apiKey": "apiKey",
        "authDomain": "hepatitis-mobile.firebaseapp.com",
        "databaseURL": "https://hepatitis-mobile.firebaseio.com",
        "storageBucket": "hepatitis-mobile.appspot.com",
        "serviceAccount":cred
        }

        storage_path = f'image/{userid}/{filename_user}'
        firebase = pyrebase.initialize_app(config)
        storage = firebase.storage()
        storage.child(storage_path).put(filepath)
        imageurl = storage.child(storage_path).get_url(current_user["userid"])
        print(imageurl)
        with connection.cursor() as cursor:
            query = f"UPDATE {table} SET imgurl = {repr(imageurl)} WHERE {table}.doctor_userid={repr(userid)}"
            
            try:
                cursor.execute(query)
                connection.commit()
                return("upload successful")
            except:
                return ("unable to upload image")



    def get_all_doctors(self):
        doctors = []
        with connection.cursor() as cursor:
            try:
                cursor.execute('show tables')
                result = cursor.fetchall()
                for items in result:
                    if items[0][-7:]=='doctors':
                        item = items[0]
                        self.hospital_name = item[:-8]
                        query = (f'SELECT * FROM {item}')
                        cursor.execute(query)
                        result = cursor.fetchall()
                        for doctor in result:
                            result = self.json(*doctor)
                            doctors.append(result)
                        
                return (doctors)
            except:
                return ("unable to get list of all doctors")
