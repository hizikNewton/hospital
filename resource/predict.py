
from flask_restful import Api,reqparse
from flask_jwt import jwt_required
import json
from flask_restful import Resource
from flask_cors import cross_origin
import dill
import pickle
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import VotingClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import Imputer
from sklearn.preprocessing import LabelEncoder,OneHotEncoder
from sklearn.preprocessing import StandardScaler
from model.patientModel import PatientModel



# Importing the dataset
dataset = pd.read_excel('./hepatitis.xlsx')
dataset.head()
dataset.shape
dataset.columns
dataset.isnull().sum()
pred_var=['GENDER','ALT','AST','AGE','HBVDNA','HBeAg','HBsAg']
X_train,X_test,y_train,y_test=train_test_split(dataset[pred_var],dataset['TARGET'], test_size=0.25,random_state=0)

#Preprocessing steps 
X_train['HBeAg']=X_train['HBeAg'].str.lower()
X_train['HBsAg']=X_train['HBsAg'].str.lower()
X_train['GENDER']=X_train['GENDER'].str.lower()
X_train['AGE']=X_train['AGE'].str.lower()

X_train['HBVDNA'].replace(['170 MILLION ','NOT DET','850 milli'],['170000000','nan','850000000'],inplace=True)
X_train['HBeAg'].replace(['postive','negative  positive'],['positive','negative'],inplace=True)
X_train['HBsAg'].replace(['not done','nan'],inplace=True)

X_train['AGE']=X_train['AGE'].str.split('yrs').str[0]
X_train['AGE']=X_train['AGE'].str.split(' ').str[0]

X_train['GENDER']=X_train['GENDER'].str.split(' ').str[0]

#X_train['TARGET']=X_train['TARGET'].fillna('A+')
X_train['HBeAg']=X_train['HBeAg'].fillna('positive')
X_train['HBsAg']=X_train['HBsAg'].fillna('negative')

X_train['AGE']=X_train['AGE'].astype(float)
X_train['HBVDNA']=X_train['HBVDNA'].astype(float)


X_train['ALT']=X_train['ALT'].fillna(X_train['ALT'].mean())
X_train['AST']=X_train['AST'].fillna(X_train['AST'].mean())
X_train['AGE']=X_train['AGE'].fillna(X_train['AGE'].mean())
X_train['HBVDNA']=X_train['HBVDNA'].fillna(X_train['HBVDNA'].mean())

'''labels_columns=['GENDER','HBeAg','HBsAg']
for _ in labels_columns:
    print("List of unique labels{}:{}".format(_,set(X_train[_])))'''
gender_values={'male':1,'female':0}
hbeag_values={'positive':1,'negative':0}
hbsag_values={'positive':1,'negative':0}

X_train.replace({'GENDER':gender_values,'HBeAg':hbeag_values,'HBsAg':hbsag_values},inplace=True)

#X_train.head()
#X_train.isnull().sum()
X_train=X_train.as_matrix()

#X_train.shape

#creating a pre-processing estimator that would help in writing better pipeline and in future deployment
from sklearn.base import BaseEstimator, TransformerMixin

class Preprocessing (BaseEstimator, TransformerMixin):
    
    def __init__(self):
        pass
    
    def transform(self,df):
        pred_var=['GENDER','ALT','AST','AGE','HBVDNA','HBeAg','HBsAg']
        
        df=df[pred_var]
        
        df['HBeAg']=df['HBeAg'].str.lower()
        df['HBsAg']=df['HBsAg'].str.lower()
        df['GENDER']=df['GENDER'].str.lower()
        #df['AGE']=df['AGE'].str.lower()

        df['HBVDNA'].replace(['170 MILLION ','NOT DET','850 milli'],[170000000,'nan',850000000],inplace=True)
        df['HBeAg'].replace(['postive','negative  positive'],['positive','negative'],inplace=True)
        df['HBsAg'].replace(['not done','nan'],inplace=True)
        
            
        df['AGE']=df['AGE'].str.split('yrs').str[0]
        df['AGE']=df['AGE'].str.split( ).str[0]
       
        
        df['AGE']=df['AGE'].astype(float)

        df['GENDER']=df['GENDER'].str.split(' ').str[0]

        #X_train['TARGET']=X_train['TARGET'].fillna('A+')
        df['HBeAg']=df['HBeAg'].fillna('positive')
        df['HBsAg']=df['HBsAg'].fillna('negative')

        
        df['HBVDNA']=df['HBVDNA'].astype(float)


        df['ALT']=df['ALT'].fillna(self.alt_mean_)
        df['AST']=df['AST'].fillna(self.ast_mean_)
        df['AGE']=df['AGE'].fillna(df['AGE'].mean())
        df['HBVDNA']=df['HBVDNA'].fillna(df['HBVDNA'].mean())
        
        gender_values={'male':1,'female':0}
        hbeag_values={'positive':1,'negative':0}
        hbsag_values={'positive':1,'negative':0}

        df.replace({'GENDER':gender_values,'HBeAg':hbeag_values,'HBsAg':hbsag_values},inplace=True)
        
        return df.as_matrix()
    def fit(self,df,y=None,**fit_params):
        
        self.alt_mean_=df['ALT'].mean()
        self.ast_mean_=df['AST'].mean()
        #self.age_mean_=df['AGE'].mean()
        #self.hbv_mean_=df['HBVDNA'].mean()
        return self
    
#To make sure it works
X_train,X_test,y_train,y_test=train_test_split(dataset[pred_var],dataset['TARGET'], test_size=0.25,random_state=42)

X_train.head()

preprocess=Preprocessing()

preprocess

preprocess.fit(X_train)

X_train_transformed=preprocess.transform(X_train)

X_train_transformed.shape

X_test_transformed=preprocess.transform(X_test)

X_train_transformed.shape


y_test=y_test.replace({'A+':1,'A-':0,'nan':1}).as_matrix()

y_train=y_train.fillna('A+')
y_train=y_train.replace({'A+':1,'A-':0}).as_matrix()

estimators = []
model1 = GaussianNB()
estimators.append(('naive', model1))
model2 = DecisionTreeClassifier()
estimators.append(('tree', model2))
model3 = SVC()
estimators.append(('svm', model3))
# create the ensemble model
#ensemble = VotingClassifier(estimators, voting='hard')

pipe=make_pipeline(Preprocessing(),
                   StandardScaler(),
                   VotingClassifier(estimators, voting='hard'))
pipe.fit(X_train,y_train)
from sklearn.externals import joblib
joblib.dump(pipe, 'piped.pkl')
loaded_model = joblib.load('piped.pkl')
'''my_data=pd.DataFrame({'GENDER':['male','female'],'ALT':[27,20],'AST':[26,30],'AGE':[40,45],'HBVDNA':[300,200],'HBeAg':['positive','negative'],'HBsAg':['positive','positive']},columns=['GENDER','ALT','AST','AGE','HBVDNA','HBeAg','HBsAg'])
my_data.as_matrix()'''
data = pd.read_excel('user.xlsx')
loaded_model.predict(X_train)
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
        with open('./model2.pkl','rb') as f:
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
