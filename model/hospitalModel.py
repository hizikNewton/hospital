import pymysql
from .userModel import UserModel

connection = pymysql.connect(host ='w29ifufy55ljjmzq.cbetxkdyhwsb.us-east-1.rds.amazonaws.com',user = 'a11ebo308uf0dhrm',port = 3306,password = 'tywq3fh90wnc0qdq',database = 'newcz2i2298jb65b')
class HospitalModel():

    myattr = ['hname','hpatients_rec','hpatients','hdoctors']

    def __init__(self,hospital_name=''):
        self.hospital_name = hospital_name
        self.patients = []
        self.doctors = []
        self.myattr = self.create_table_data(hospital_name)
        HospitalModel.myattr = self.myattr

    def create_table_data(self,hospital_name):
        hospital_name = hospital_name.replace(' ','_')
        hpatients = '{hp}_patients'.format(hp=hospital_name)
        hpatients_rec = '{hp}_patients_rec'.format(hp=hospital_name)
        hdoctors = '{hp}_doctors'.format(hp=hospital_name)
        myattrVal = {'hospital_name':hospital_name,'hdoctors':hdoctors,'hpatients':hpatients,'hpatients_rec':hpatients_rec}

        return (myattrVal)

    def create_hospital(self,hospital_name):
        tableitem = self.myattr
        
        create_hospital = "CREATE TABLE IF NOT EXISTS {hospital}(id MEDIUMINT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT)".format(hospital=tableitem['hospital_name'])

        create_doctor_table = "CREATE TABLE IF NOT EXISTS {hospital_doctors}(id MEDIUMINT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,doctor_userid VARCHAR(10),doctor_surname VARCHAR(40),doctor_name VARCHAR(40),specialization VARCHAR(40),biodata TEXT,timestamp DATETIME)".format(hospital_doctors=tableitem['hdoctors'])

        create_patient_table = "CREATE TABLE IF NOT EXISTS {hospital_patients}(id MEDIUMINT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,patient_name VARCHAR(40),record TEXT,category VARCHAR(40),doctor_id MEDIUMINT,FOREIGN KEY(doctor_id) REFERENCES {doctors}(id) ON DELETE CASCADE)".format(hospital_patients=tableitem['hpatients'],doctors=tableitem['hdoctors'],patient_rec = tableitem['hpatients_rec'] )
        user = UserModel()
        with connection.cursor() as cursor:
            
            try: 
                
                cursor.execute(create_hospital)
                cursor.execute(create_doctor_table)
                cursor.execute(create_patient_table)
                cursor.execute(user.create_user_table())
                
                
            except:
                return ('cannot create {hospital} hospital'.format(hospital = hospital_name)),503
            return('Hospital {hospital} created succesfully'.format(hospital = hospital_name)),201
    


    def check_hospital_exist(self,hospital_name):
        with connection.cursor() as cursor:
            query = "SELECT id from {name}".format(name = hospital_name)
            try:
                cursor.execute('{q}'.format(q=query))
            except:
                result = False
                return result
            else:
                result = True
                return result


    def json(self,doctor_name,patient_name,**kwargs):
        item = {
        "Doctors":doctor_name,
        "Patients":patient_name,
         } 
        return(item),200
        

    def get_hospital(self,hospital_name):
        with connection.cursor() as cursor:
            if(self.check_hospital_exist):
                name=hospital_name
                try:
                    cursor.execute(f'SELECT doctor_name FROM {name}_doctors')
                except:
                    return ('cannot get {name}'.format(name = hospital_name))
                else:
                    row = cursor.fetchall()
                    cursor.execute(f'SELECT patient_name FROM {name}_patients')
                    row2 = cursor.fetchall()
                    for item in row:
                        self.doctors.append(item[0])
                    for item in row2:
                        self.patients.append(item[0])
                    return(self.json(doctor_name=self.doctors,patient_name=self.patients))
        connection.close()

    def get_all_hospital(self):
        hospitals = []
        with connection.cursor() as cursor:
            try:
                cursor.execute('show tables')
                result = cursor.fetchall()
                for i in result:
                    if(result.index(i)%3==0):
                        hospitals.append(i[0])
                return hospitals[:-1]
            except:
                return("cannot get list of hospital name")
        connection.close()
    
    def update_hospital(self,new_name):
        table =  self.create_table_data(self.hospital_name)
        new_table = self.create_table_data(new_name)
        with connection.cursor() as cursor:
            query = 'RENAME TABLE {hospital_name} TO {new_name}'.format(hospital_name = table['hospital_name'],new_name = new_table['hospital_name'])
            query1 = 'RENAME TABLE {hpatients} TO {new_name}'.format(hpatients=table['hpatients'],new_name = new_table['hpatients'])
            query2 = 'RENAME TABLE {hdoctors} TO {new_name}'.format(hdoctors = table['hdoctors'],new_name = new_table['hdoctors'])
            try:
                cursor.execute(query)
                cursor.execute(query1)
                cursor.execute(query2)
            except:
                return ("unable to rename hospital name"),503
            
            return "{hospital_name} hospital renamed to {new_name} hospital".format(hospital_name=self.hospital_name,new_name= new_name),200

    def delete_hospital(self):
        if self.check_hospital_exist:
            
            with connection.cursor() as cursor:
                table =  self.create_table_data(self.hospital_name)
                query = 'DROP TABLE {hospital_name}'.format(hospital_name = table['hospital_name'])
                query1 = 'DROP TABLE {hpatients}'.format(hpatients=table['hpatients'])
                query2 = 'DROP TABLE {hdoctors}'.format(hdoctors = table['hdoctors'])
                try:
                    cursor.execute(query)
                    cursor.execute(query1)
                    cursor.execute(query2)
                    return("Hospital deleted succesfully"),200
                except:
                    return ("cannot delete hospital"),503

        else:
            return("Hospital does not exist"),404


        