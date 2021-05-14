from flask_restful import Resource
from flask import request
from app import mongo
import bson
from bson.json_util import dumps
import json
from datetime import datetime


class MetaData(Resource):
    def get(self):
        user_id = request.headers.get('id')
        grid_id= request.headers.get('grid_id')
        cell_id= request.headers.get('cell_id')
        sheet_name = request.headers.get('sheet_name')
        user_object_id = bson.ObjectId(user_id)
        user = mongo.db.mdi_plus_users.find_one({'_id': user_object_id })
        if user is not None:
            entry = mongo.db.mdi_plus_meta_data.find_one({"grid_id":grid_id, "cell_id":cell_id, "sheet_name":sheet_name})
            print(entry)
            if entry is not None:
                notes = json.loads(dumps(entry["notes"]))
                return {'status':True, 'data':notes}
            else:
                return {'status':True, 'data':[]}
        else:
            return {'status':True, 'data':[]}

    def post(self):
        json_data = request.get_json(force=True)
        user_object_id = bson.ObjectId(json_data['id'])
        user = mongo.db.mdi_plus_users.find_one({'_id': user_object_id })
        grid_id= request.headers.get('grid_id')
        cell_id= request.headers.get('cell_id')
        sheet_name = request.headers.get('sheet_name')
        if user is not None:
            notes_list = []
            notes_list.append(json_data["notes"])
            metadata = mongo.db.mdi_plus_meta_data.find_one({"grid_id":grid_id, "cell_id":cell_id, "sheet_name":sheet_name})
            if metadata is None:
                mongo.db.mdi_plus_meta_data.insert(
                    {
                        'grid_id' : json_data['grid_id'],
                        'cell_id':json_data["cell_id"],
                        'sheet_name':json_data["sheet_name"],
                        'attribute_name':json_data["attribute_name"],
                        'notes' : notes_list,
                        "created_at" :datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f'),
                        "updated_at" :datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')            
                    }
                )
                return {"status": True, "message":"Measures saved successfully"}
            else:
                metadata["notes"].append(json_data["notes"])
                #print(metadata["notes"])
                try:
                    mongo.db.mdi_plus_meta_data.update_one(
                            {
                            'grid_id' : json_data['grid_id'],
                            'cell_id':json_data["cell_id"],
                            'sheet_name':json_data["sheet_name"],
                            },
                            {
                            '$set' :
                            {
                                'notes' : metadata["notes"],
                                'updated_at' : datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')  
                            }
                    })
                except Exception as ex:
                    print(ex.message)
                return {"status": True, "message":"Measures updated successfully"}
        else:
            return {'status':False, 'message':'Not a valid user'}