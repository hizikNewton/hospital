import pymysql
import datetime
from .userModel import UserModel
import uuid
from werkzeug.security import generate_password_hash

import os
import boto3
from botocore.client import Config


connection = pymysql.connect(host ='w29ifufy55ljjmzq.cbetxkdyhwsb.us-east-1.rds.amazonaws.com',user= 'uv1eihe9iofpoot5',port = 3306,password = 'ovykxit5f71gx86b',database = 'vzcwzzkfkigclq3d')
class DoctorModel:
    
    def __init__(self,hospital_name,doctor_surname='',doctor_name='',spec='',biodata=''):
        self.doctor_name = doctor_name
        self.doctor_surname = doctor_surname
        self.hospital_name = hospital_name.lower()
        self.spec = spec.lower()
        self.biodata = biodata.lower()
        self.table = '{name}_doctors'.format(name=hospital_name)
        self.user = UserModel()
        self.timestamp = datetime.datetime.now().isoformat(timespec='seconds')


    def json(self,*args):
        return {"id":args[0],
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
            password = generate_password_hash(surname) 
            imgurl = 'https://s3.us-east-2.amazonaws.com/hospital-bucket/default-doctor.jpg'
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
            print(query)
            cursor.execute(query)
            connection.commit()

    def get_doctor_record(self,id,hospital_name,dbcolumn='*'):
        if (self.check_id(id)):
            with connection.cursor() as cursor:
                dbcolumn=dbcolumn
                query=('SELECT {dbcolumn} FROM {name}_doctors WHERE id={id}'.format(name=hospital_name,dbcolumn=dbcolumn,id=id))
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
                connection.close()
        else:
            return ("id not found"),404


    def check_id(self,id):
        table = self.table
        with connection.cursor() as cursor:
            query = (f'SELECT id from {table}')
            cursor.execute(query)
            result = []
            res = cursor.fetchall()
            for i in res:
                result.append(i[0])
            if (id in result):
                return(True)
            else:
                return(False)
                


    def update_doctor_record(self,id,updatedict):
        if (self.check_id(id)):
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
                    id=id
                    query = f"UPDATE {table} SET {key} = {repr(updateitem)} WHERE {table}.id={id}"
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


    def delete_doctor_rec(self,id):
        if (self.check_id(id)):
            table = self.table
            id = id
            with connection.cursor() as cursor:
                query = (f"DELETE FROM {table} WHERE {table}.id = {id}")
                cursor.execute(query)
                connection.commit()
                return("Record deleted successfully")
        else:
            return("id not found"),404

            

    def uploadImg(self,filepath,id):
        table = self.table
        file_name = os.path.basename(filepath)
        ACCESS_KEY_ID = 'AKIAJJIDJDFNP3PUNJZQ'
        ACCESS_SECRET_KEY = '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'
        BUCKET_NAME = 'hospital-bucket'
        FILE_NAME = file_name


        data = open(filepath, 'rb')

# S3 Connect
        s3 = boto3.resource(
        's3',
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=ACCESS_SECRET_KEY,
        config=Config(signature_version='s3v4')
        )

# Image Uploaded
        s3.Bucket(BUCKET_NAME).put_object(Key=FILE_NAME, Body=data, ACL='public-read')
        imgurl = os.path.join("https://s3.us-east-2.amazonaws.com/hospital-bucket/",file_name)
        with connection.cursor() as cursor:
            query = f"UPDATE {table} SET imgurl = {repr(imgurl)} WHERE {table}.id={id}"
            
            try:
                cursor.execute(query)
                connection.commit()
                return("upload successful")
            except:
                return ("unable to upload image")

