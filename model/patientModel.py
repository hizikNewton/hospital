import pymysql
from werkzeug.security import generate_password_hash
from firebase import firebase
from google.cloud import storage
from google.cloud.storage import client
import firebase_admin
import pyrebase
from firebase_admin import credentials,storage,auth
from mycred import cred
import datetime

connection = pymysql.connect(host ='er7lx9km02rjyf3n.cbetxkdyhwsb.us-east-1.rds.amazonaws.com',user= 'v98vj2rnkd8xjsbn',port = 3306,password = 'juvam2griraafgz2',database = 'ec40ra1bb5ef3pkr')
import random as r


class PatientModel():

    
    def __init__(self,hospital_name,patient_surname='',patient_name='',record='',id='',treatingdoc=0,*kwargs):
        self.patient_name = patient_name
        self.patient_surname = patient_surname
        self.hospital_name = hospital_name
        self.record = record
        self.treatingdoc = treatingdoc
        self.table = '{name}_patients'.format(name=hospital_name)
        self.id = id
        self.timestamp = datetime.datetime.now().isoformat(timespec='seconds')

    def json(self,id,surname,name,imgurl,record,biodata,timestamp,category,treatingdoc_name):
        return {
            'id':id,
            'surname':surname,
            'name':name,
            'imgurl':imgurl,
            'record':record,
            'biodata':biodata,
            'timestamp':timestamp,
            'category':category,
            'treatingdoc_name':treatingdoc_name
        }

    def insert_patient(self,category,treatingdoc):
        treatingdoc = self.get_treating_doctor(category)
        table = self.table
        patient_surname = self.patient_surname
        patient_name = self.patient_name
        record = self.record
        category = category
        treatingdoc = treatingdoc
        with connection.cursor() as cursor:
            query = f"INSERT INTO {table} (patient_surname,patient_name,record,category,doctor_id)VALUES({repr(patient_surname)},{repr(patient_name)},{repr(record)},{repr(category)},{repr(treatingdoc)})"
            cursor.execute(query)
            connection.commit()

    def get_last_id(self,hospital_name):
        cursor = connection.cursor()
        query=('SELECT id FROM {name}_patients'.format(name=hospital_name))
        result=cursor.execute(query)
        result = result.fetchall()
        result = len(result)
        return result
 

    def get_treating_doctor(self,category):
        table_name = "({0}_doctors)".format(self.hospital_name)
        name=self.hospital_name
        category = category
        with connection.cursor() as cursor:
            query=(f'SELECT id FROM {name}_doctors WHERE specialization={repr(category)}')
            cursor.execute(query)

            result = cursor.fetchall()
            if result:
                rx = r.choice(result)
                return(rx[0])
            else:
                return 0
            connection.close()


    def get_patient(self,id,hospital_name):
        cursor = connection.cursor()
        query=('SELECT * FROM {name}_patients WHERE id={id}'.format(name=hospital_name,id=id))
        try:
            cursor.execute(query)
        except:
            return ('cannot get requested patient')
        else:
            cursor.execute(query)
            result = cursor.fetchone()
            if (result==None):
                return('No Patient with this id')
            treatingdoc_id = result[-1]
            treatingdoc=cursor.execute(('SELECT * FROM {name}_doctors WHERE id={id}'.format(name=hospital_name,id = treatingdoc_id)))
            if (treatingdoc_id==0):
                return(result,"{name} has no doctor".format(name=result[1]))
            else:
                cursor.execute(('SELECT * FROM {name}_doctors WHERE id={id}'.format(name=hospital_name,id = treatingdoc_id)))
                treatingdoc=cursor.fetchone()
                treatingdoc_name = treatingdoc[2]+' '+treatingdoc[3]
                return(self.json(result[0],result[1],result[2],result[3],result[4],result[5],result[6],result[7],treatingdoc_name))
        connection.close()


    def get_all_patient(self,hospital_name):
        patient_list = []
        with connection.cursor() as cursor:
            query=('SELECT * FROM {name}_patients'.format(name=hospital_name))
            try:
                cursor.execute(query)
            except:
                return ('cannot get list of patients')
            else:
                cursor.execute(query)
                result = cursor.fetchall()
                for patient in result:
                    treatingdoc_id = patient[-1]
                    treatingdoc=cursor.execute(('SELECT * FROM {name}_doctors WHERE id={id}'.format(name=hospital_name,id = treatingdoc_id)))
                    if (treatingdoc_id==0):
                        patient_list.append(self.json(patient[1],patient[2],'No Doctor Assigned'))
                    else:
                        cursor.execute(('SELECT * FROM {name}_doctors WHERE id={id}'.format(name=hospital_name,id = treatingdoc_id)))
                        treatingdoc=cursor.fetchone()
                        treatingdoc_name = treatingdoc[2]+' '+treatingdoc[3]
                        patient_list.append(self.json(patient[0],patient[1],patient[2],patient[3],patient[4],patient[5],patient[6],patient[7],treatingdoc_name))
                return patient_list
        connection.close()

    def get_patient_record(self,id,hospital_name):
        cursor = connection.cursor()
        query=('SELECT record FROM {name}_patient WHERE id={id}'.format(name=hospital_name,id=id))
        try:
            cursor.execute(query)
        except:
            return ('cannot get requested doctor record')
        else:
            result = cursor.execute(query)
            result = result.fetchone()
            return(self.json(*result))
        connection.close()



    def check_id(self,id):
        table = self.table
        result = []
        with connection.cursor() as cursor:
            query = (f'SELECT id from {table}')
            cursor.execute(query)
            
            res = cursor.fetchall()
            for i in res:
                result.append(i[0])
            if (id in result):
                return(True)
            else:
                return(False)
                


    def update_patient_record(self,id,updatedict):
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
                    cursor.execute(item)
                    try:
                        cursor.execute(item)
                        connection.commit()
                    except:
                        return("Unable to update record")
                return("Record updated successfully")
        else:
            return ("id not found"),404


    def delete_patient_rec(self,id):
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


    def uploadwithPyre(self,filepath,secretkey,id):
        table = self.table
        cred['private_key'] = secretkey
        
        config = {
        "apiKey": "apiKey",
        "authDomain": "hepatitis-mobile.firebaseapp.com",
        "databaseURL": "https://hepatitis-mobile.firebaseio.com",
        "storageBucket": "hepatitis-mobile.appspot.com",
        "serviceAccount":cred
        }

        storage_path = f'image/patient/{id}/'
        firebase = pyrebase.initialize_app(config)
        storage = firebase.storage()
        storage.child(storage_path).put(filepath)
        imageurl = storage.child(storage_path).get_url(id)
        
        with connection.cursor() as cursor:
            query = f"UPDATE {table} SET imgurl = {repr(imageurl)} WHERE {table}.id={repr(id)}"
            
            try:
                cursor.execute(query)
                connection.commit()
                return("upload successful")
            except:
                return ("unable to upload image")