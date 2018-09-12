import pymysql
import datetime
from .userModel import UserModel
import uuid
from werkzeug.security import generate_password_hash


connection = pymysql.connect(host ='w29ifufy55ljjmzq.cbetxkdyhwsb.us-east-1.rds.amazonaws.com',user= 'a11ebo308uf0dhrm',port = 3306,password = 'tywq3fh90wnc0qdq',database = 'newcz2i2298jb65b')
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
        "biodata":args[5]
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
            self.user.insert_user(doctor_userid,username,password,timestamp)
            query = f"INSERT INTO {table} (doctor_userid,doctor_name,doctor_surname,specialization,biodata,timestamp)VALUES({repr(doctor_userid)},{repr(name)},{repr(surname)},{repr(spec)},{repr(biodata)},{repr(timestamp)})"
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

            

