from flask_restful import Api,reqparse
from flask_jwt import jwt_required
import json
from flask_restful import Resource
from model.recordModel import RecordModel

class Record(Resource):
    def post(self,hospital_name):
        parser = reqparse.RequestParser()
        parser.add_argument(
        'record_path',
        type = str,
        required = True,
        help = 'Path to record required'
        )
        data = parser.parse_args()
        rec_path = data['record_path']
        inst_rec = RecordModel()
        inst_rec.loadCSV(rec_path)
        return ("record loaded")
