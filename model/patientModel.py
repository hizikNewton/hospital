import pymysql


connection = pymysql.connect(host ='w29ifufy55ljjmzq.cbetxkdyhwsb.us-east-1.rds.amazonaws.com',user = 'a11ebo308uf0dhrm',port = 3306,password = 'tywq3fh90wnc0qdq',database = 'newcz2i2298jb65b')
import random as r


class PatientModel():

    
    def __init__(self,hospital_name,patient_name='',record='',treatingdoc=0,**args):
        self.patient_name = patient_name
        self.hospital_name = hospital_name
        self.record = record
        self.treatingdoc = treatingdoc
        self.table = '{name}_patients'.format(name=hospital_name)

    def json(self,name,record,treatingdoc_name):
        return {
            "Name":name,
            "Record":record,
            "Treating Doctor":treatingdoc_name
        }

    def insert_patient(self,category,treatingdoc):
        with connection.cursor() as cursor:
            query = "INSERT INTO {!s} (patient_name,record,category,doctor_id) VALUES ({!r},{!r},{!r},{!r})".format(self.table,self.patient_name,self.record,category,treatingdoc)
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
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM {table_name} where specialization="{category}"'.format(table_name=table_name,category = category))
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
                return(self.json(result[1],result[2],treatingdoc_name))
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
                        patient_list.append(self.json(patient[1],patient[2],treatingdoc_name))
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