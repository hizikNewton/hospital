from flask_jwt import jwt_required,JWT,jwt
import uuid
from werkzeug.security import generate_password_hash,check_password_hash
from flask import make_response
import pymysql
import datetime
from functools import wraps 

connection = pymysql.connect(host ='w29ifufy55ljjmzq.cbetxkdyhwsb.us-east-1.rds.amazonaws.com',user = 'a11ebo308uf0dhrm',port = 3306,password = 'tywq3fh90wnc0qdq',database = 'newcz2i2298jb65b')

from flask_restful import reqparse,Resource,request


class UserModel():

    def find_by_username(self,username):
        with connection.cursor() as cursor:
            username = username
            query = f"SELECT * FROM users WHERE username={repr(username)}"
            cursor.execute(query)
            row = cursor.fetchone()
            if row:
                user = True 
            else:
                user = None
            return user



    @classmethod
    def find_by_id(cls,_id):
        with connection.cursor() as cursor:
            query = "SELECT * FROM users WHERE id={id}"
            cursor.execute(query)
            row = cursor.fetchone()
            if row:
                user = cls(*row)
            else:
                user = None
            return user


    def create_user_table(self):
            user_table = "CREATE TABLE IF NOT EXISTS users(id MEDIUMINT(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,userid VARCHAR(50) NOT NULL,username VARCHAR(50) NOT NULL,password VARCHAR(256) NOT NULL,isdoctor BOOLEAN,admin BOOLEAN,create_date DATETIME)"
            return user_table



    def create_user(self,username,password):
        create_date = datetime.datetime.now().isoformat(timespec='seconds')
        create_date = create_date.replace('T',' ')
        username = username
        password = generate_password_hash(password)
        userid = str(uuid.uuid4())
        userid = userid[0:8]
        admin = False
        isdoctor = False
        
        
        if (self.find_by_username(username)):
            return {"message":"username exist"},400
        else:
            with connection.cursor() as cursor:
                query  = f"INSERT INTO users(userid,username,password,isdoctor,admin,create_date) VALUES ({repr(userid)},{repr(username)},{repr(password)},{isdoctor},{admin},{repr(create_date)})"
                cursor.execute(query)
                connection.commit()
                
                return {"message":"user created succesfully"},201


    def insert_user(self,userid,username,password,create_date):
        if (self.find_by_username(username)):
            return {"message":"username exist"},400
        else:
            isdoctor=True
            admin=False
            with connection.cursor() as cursor:
                query  = f"INSERT INTO users(userid,username,password,isdoctor,admin,create_date) VALUES ({repr(userid)},{repr(username)},{repr(password)},{isdoctor},{admin},{repr(create_date)})"
                cursor.execute(query)
                connection.commit()
                
                return {"message":"user created succesfully"},201
                

    def check_(self,dbtable_col,value_to_check):
        table_col = dbtable_col
        value = value_to_check
        table = 'users'
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


    def json(self,*args):
        user = {
        "id":args[0],
        "userid":args[1],
        "username":args[2],
        "password":args[3],
        "isdoctor":args[4],
        "admin":args[5],
        "date":args[6].isoformat()
        }
        return(user)


    def get_one(self,dbtable_col,value_to_get):
        table_col = dbtable_col
        value = value_to_get
        if(self.check_(table_col,value)):
            with connection.cursor() as cursor:
                query = f'SELECT * FROM users WHERE {(table_col)} = {repr(value)}'
                cursor.execute(query)
                user = cursor.fetchone()
                user = self.json(*user)
                return user
        
            

    def promote_user_doc(self,userid):
        if(self.check_('userid',userid)):
            with connection.cursor() as cursor:
                userid = userid
                isdoctor = True
                query = f"UPDATE users SET users.isdoctor = {isdoctor} WHERE users.userid={repr(userid)}"
                cursor.execute(query)
                connection.commit()
            return("User promoted to doctor")
        else:
            return('id not found'),404


    def promote_user_admin(self,userid):
        if(self.check_('userid',userid)):
            with connection.cursor() as cursor:
                userid = userid
                admin = True
                query = f"UPDATE users SET users.admin = {admin} WHERE users.userid={repr(userid)}"
                cursor.execute(query)
                connection.commit()
            return("User promoted to admin")
        else:
            return('id not found'),404


    def delete_user(self,userid):
        if (self.check_("userid",userid)):
            table = 'users'
            with connection.cursor() as cursor:
                query = (f"DELETE FROM {table} WHERE {table}.userid = {repr(userid)}")
                cursor.execute(query)
                connection.commit()
                return("User deleted successfully")
        else:
            return("id not found"),404


    '''def delete_user_table(self):
        with connection.cursor() as cursor:
            query = ("DROP TABLE users")
            try:
                cursor.execute(query)
                connection.commit()
            except:
                return({"message":"Error deleting table user"})
            return({"message":"User table deleted successfully"}),200'''

    def login(self,auth):
        if (not auth or not auth['username'] or not auth['password']):
            return make_response("provide username/password",401,{'WWW-Authenticate':'Basic Realm="Login Required!'})
        user = self.get_one('username',auth['username'])

        if not user:
            return make_response("incorrect username/password",401,{'WWW-Authenticate':'Basic Realm="Login Required!'})
        if  check_password_hash(user['password'],auth['password']):
            token = jwt.encode({"user_id":user['userid'],"exp":datetime.datetime.utcnow() + datetime.timedelta(minutes = 1000)},'OLURIN ANUOLUWAPO')
            
            return ({"token":f"{token}"})

        else:
            return make_response("invalid password",401,{'WWW-Authenticate':'Basic Realm="Login Required!'})


    def token_required(f):
        @wraps(f)
        def decorated(*args,**kwargs):
            token = None
            if 'x-access-token' in request.headers:
                token = request.headers['x-access-token']
            if not token:
                return ({"message":"token is missing"}),401

            data = jwt.decode(token,'OLURIN ANUOLUWAPO')
            try:
                current_user = UserModel().get_one('userid',data['user_id'])
            except:
                return ({"message":"token is invalid"}),401

            return f(current_user,*args,**kwargs)

        return decorated

        

