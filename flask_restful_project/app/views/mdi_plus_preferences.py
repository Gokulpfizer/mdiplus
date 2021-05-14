from flask_restful import Resource
from flask import request
from app import mongo
import bson
from bson.json_util import dumps
import json
from datetime import datetime

class PreferenceCells(Resource):
    def get(self):
        user_id = request.headers.get('id')
        grid_id= request.headers.get('grid_id')
        cell_id= request.headers.get('cell_id')
        sheet_name = request.headers.get('sheet_name')
        user_object_id = bson.ObjectId(user_id)
        user = mongo.db.mdi_plus_users.find_one({'_id': user_object_id })
        if user is not None:
            entry = mongo.db.mdi_plus_cell.find_one({"data_grid_id":grid_id, "cell_id":cell_id, "sheet_name":sheet_name})
            if entry is not None:
                preferences = entry['preferences']
                d={}
                for p in preferences:
                    d[p['preference_name']] = p['preference_value']
                return {'status':True, 'data':dumps(d)}
            else:
                return {'status':False, 'data':dumps({})}
        else:
            return {'status':False, 'data':dumps({})}

    def post(self):
        json_data = request.get_json(force=True)
        user_object_id = bson.ObjectId(json_data['id'])
        user = mongo.db.mdi_plus_users.find_one({'_id': user_object_id })
        if user is not None:
            preferences = mongo.db.mdi_plus_cell.find_one({"data_grid_id":json_data['grid_id'], "cell_id":json_data["cell_id"], "sheet_name":json_data["sheet_name"]})
            if preferences is None:
                notes_list = []
                notes_list.append(json_data["notes"])
                preferences_data =[]
                for p in ['value','lower_95_ci','upper_95_ci','source_document','notes','qc_status','description']:
                    if p == 'notes':
                        d = {}
                        d['preference_name'] = p
                        d['preference_value'] = notes_list
                        preferences_data.append(d)
                    else:
                        d = {}
                        d['preference_name'] = p
                        d['preference_value'] = json_data[p]
                        preferences_data.append(d)
                mongo.db.mdi_plus_cell.insert(
                    {
                        'data_grid_id' : json_data['grid_id'],
                        'project_id' : json_data['project_id'],
                        'cell_id':json_data["cell_id"],
                        'sheet_name':json_data["sheet_name"],
                        'preference_header':json_data["attribute_name"],
                        'row_attribute_value':json_data["row_attribute_value"],
                        'preferences': preferences_data,
                        "created_at" :datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f'),
                        "updated_at" :datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')            
                    }
                )
                return {"status": True, "message":"Preferences saved successfully"}
            else:
                notes_list = []
                for ps in preferences['preferences']:
                    if ps['preference_name'] == 'notes':
                        notes_list.append(ps['preference_value'])
                notes_list[0].append(json_data["notes"])
                preferences_data =[]
                for p in ['value','lower_95_ci','upper_95_ci','source_document','notes','qc_status','description']:
                    if p == 'notes':
                        d = {}
                        d['preference_name'] = p
                        d['preference_value'] = notes_list[0]
                        preferences_data.append(d)
                    else:
                        d = {}
                        d['preference_name'] = p
                        d['preference_value'] = json_data[p]
                        preferences_data.append(d)
                try:
                    mongo.db.mdi_plus_cell.update_one(
                            {
                            'data_grid_id' : json_data['grid_id'],
                            'cell_id':json_data["cell_id"],
                            'sheet_name':json_data["sheet_name"],
                            },
                            {
                            '$set' :
                            {
                                'preferences' : preferences_data,
                                'updated_at' : datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')  
                            }
                    })
                except Exception as ex:
                    print(ex.message)
                return {"status": True, "message":"Preferences updated successfully"}
        else:
            return {'status':False, 'message':'Not a valid user'}