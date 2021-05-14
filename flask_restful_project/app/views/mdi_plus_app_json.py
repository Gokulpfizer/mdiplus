from flask_restful import Resource
from flask import request
from app import mongo
import bson
from bson.json_util import dumps
import json
from datetime import datetime


class MdiPlusAppJson(Resource):
    def get(self):
        uid = request.headers.get('id')
        project_id = request.headers.get('project_id')
        user_object_id = bson.ObjectId(uid)
        user = mongo.db.mdi_plus_users.find_one({'_id': user_object_id })
        if user is not None:
            entry = mongo.db.mdi_plus_app_json.find_one({'project_id':project_id, 'user_id': uid})
            if entry is None:
                entries = mongo.db.mdi_plus_projects.find_one({'_id':bson.ObjectId(project_id)})
                print(entries)
                for c in entries["collaborators"]:
                    #print(c['collaborator'])
                    if c['collaborator'] == user['username']:
                        #print(project_id)
                        entry = mongo.db.mdi_plus_app_json.find_one({'project_id':project_id})
                        if entry is not None:
                            Grid = json.loads(dumps(entry["json_file"]))
                            #print(Grid)
                            return {"status": True, "data": Grid,"grid_id":str(entry["_id"])}
            else:
                Grid = json.loads(dumps(entry["json_file"]))
                return {"status": True, "data": Grid, "grid_id":str(entry["_id"])}
        else:
            return {'status':True, 'data':[]}
    def post(self):
        json_data = request.get_json(force=True)
        user_object_id = bson.ObjectId(json_data['id'])
        user = mongo.db.mdi_plus_users.find_one({'_id': user_object_id })
        if user is not None:
            project = mongo.db.mdi_plus_app_json.find_one({"user_id": json_data['id'], "project_id":json_data["project_id"]})
            if project is None:
                mongo.db.mdi_plus_app_json.insert(
                    {
                        'user_id' : json_data['id'],
                        'project_id':json_data["project_id"],
                        'json_file' : json_data["json_file"],
                        "created_at" :datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f'),
                        "updated_at" :datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f'),            
                    }
                )
                return {"status": True, "message":"Grid saved successfully"}
            else:
                try:
                    mongo.db.mdi_plus_app_json.update_one(
                            {
                            'user_id' : json_data['id'],
                            'project_id':json_data["project_id"]
                            },
                            {
                            '$set' :
                            {
                                'json_file' : json_data["json_file"],
                                'updated_at' : datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')  
                            }
                    })
                except Exception as ex:
                    print(ex.message)
                return {"status": True, "message":"Grid updated successfully"}
        else:
            return {'status':False, 'message':'Not a valid user'}
        