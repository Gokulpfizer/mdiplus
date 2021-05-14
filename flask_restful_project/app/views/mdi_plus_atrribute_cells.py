from flask_restful import Resource
from flask import request
from app import mongo
import bson
from bson.json_util import dumps
import json
from datetime import datetime



class ReadProjectCells(Resource):
    def post(self):
        _json = request.json
        find_entries = mongo.db.mdi_plus_cell.aggregate([{ "$match": { 'data_grid_id': str(_json["data_grid_id"]) } }, {"$group": { "_id":{ "name":"$sheet_name", "row_id": "$row_id"}, "row_id": { "$first" : "$row_id" },"name": { "$first" : "$sheet_name" } , "cells": { "$push" : "$cell_data" } } }, { "$sort": { "row_id": 1 } },  ])
        if find_entries is not None: 
                _content = list(json.loads(dumps(find_entries)))
                return { "rows": _content }
        else:
            _message = "mdi plus cell got successfully"
            return _message

class MultiAttributeCells(Resource):
    def post(self):
        _json = request.json
        print(_json)
        data_grid_id = str(_json['data_grid_id'])
        sheet_name = str(_json['sheet_name'])
        # mongo.db.mdi_plus_cell.remove({"data_grid_id":data_grid_id, "sheet_name":sheet_name})
        for entry in _json["cell_info"]:
            print("----")
            print(entry)
            cell_data = json.loads(dumps(mongo.db.mdi_plus_cell.find_one({"data_grid_id":data_grid_id, "row_id":entry["row_id"], "column_id": entry["column_id"] ,"sheet_name":entry["sheet_name"]}) ))
            print("----")
            print(cell_data)
            print("----=================")

            if cell_data is not None:
                mongo.db.mdi_plus_cell.update({"data_grid_id": data_grid_id, "row_id":entry["row_id"], "cell_id": entry["column_id"] ,"sheet_name":entry["sheet_name"]}, {"$set": {"cell_data": entry["cell_data"]} })
            else:
                mongo.db.mdi_plus_cell.insert(entry)
        _message = "Table created successfully"
        return _message

class Attributecells(Resource):

    # def mdi_plus_cell_entry():
    #     _json = request.json
    #     print(_json)
    #     err = validate_mdi_plus_cell(_json)
    #     print(err)
    #     if err is None:
    #         print(_json)
    #         cell_id = _json['cell_id']
    #         project_id = str(_json['project_id'])
    #         data_grid_id = str(_json['data_grid_id'])
    #         comparator_id = str(_json['comparator_id'])
    #         find_count = mongo.db.mdi_plus_cell.count({ "cell_id": cell_id, "comparator_id":comparator_id, "project_id": project_id})
    #         _id = getId(_json)
    #         if _id is not None:
    #             del _json['_id']
    #         if find_count != 0:
    #             mongo.db.mdi_plus_cell.remove({ "cell_id": cell_id, "comparator_id":comparator_id, "project_id": project_id})
    #         _json['created_at'] = get_current_time_stamp()
    #         mongo.db.mdi_plus_cell.insert(
    #             _json
    #         )        
    #         _message = "Table created successfully"
    #         return base_response(_message)
    #     else:
    #         print(err)
    #         return send_error(err)

    

    def get(self):
        user_id = request.headers.get('id')
        grid_id= request.headers.get('grid_id')
        cell_id= request.headers.get('cell_id')
        sheet_name = request.headers.get('sheet_name')
        user_object_id = bson.ObjectId(user_id)
        user = mongo.db.mdi_plus_users.find_one({'_id': user_object_id })
        if user is not None:
            entry = mongo.db.mdi_plus_cell.find_one({"grid_id":grid_id, "cell_id":cell_id, "sheet_name":sheet_name})
            if entry is not None:
                attributes = entry['attributes']
                d={}
                for a in attributes:
                    d[a['attribute_name']] = a['attribute_value']
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
            attributes = mongo.db.mdi_plus_cell.find_one({"grid_id":json_data['grid_id'], "cell_id":json_data["cell_id"], "sheet_name":json_data["sheet_name"]})
            if attributes is None:
                notes_list = []
                notes_list.append(json_data["notes"])
                attributes_data =[]
                for a in ['type','attribute','timepoint','definition','unit','rationale_for_attribute','rationale_for_timepoint',\
                        'rationale_for_definition_and_unit','notes','qc_status']:
                    if a == 'notes':
                        d = {}
                        d['attribute_name'] = a
                        d['attribute_value'] = notes_list
                        attributes_data.append(d)
                    else:
                        d = {}
                        d['attribute_name'] = a
                        d['attribute_value'] = json_data[a]
                        attributes_data.append(d)
                mongo.db.mdi_plus_cell.insert(
                    {
                        'grid_id' : json_data['grid_id'],
                        'cell_id':json_data["cell_id"],
                        'sheet_name':json_data["sheet_name"],
                        'attribute_header':json_data["attribute_name"],
                        'row_attribute_value':json_data["row_attribute_value"],
                        'attributes': attributes_data,
                        "created_at" :datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f'),
                        "updated_at" :datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')            
                    }
                )
                return {"status": True, "message":"Attributes saved successfully"}
            else:
                notes_list = []
                for ats in attributes['attributes']:
                    if ats['attribute_name'] == 'notes':
                        print('in if', ats['attribute_value'])
                        notes_list.append(ats['attribute_value'])
                notes_list[0].append(json_data["notes"])
                print('after if ',notes_list)
                attributes_data =[]
                for a in ['type','attribute','timepoint','definition','unit','rationale_for_attribute','rationale_for_timepoint',\
                        'rationale_for_definition_and_unit','notes','qc_status']:
                    if a == 'notes':
                        d = {}
                        d['attribute_name'] = a
                        d['attribute_value'] = notes_list[0]
                        attributes_data.append(d)
                    else:
                        d = {}
                        d['attribute_name'] = a
                        d['attribute_value'] = json_data[a]
                        attributes_data.append(d)
                #print(attributes_data)
                try:
                    mongo.db.mdi_plus_cell.update_one(
                            {
                            'grid_id' : json_data['grid_id'],
                            'cell_id':json_data["cell_id"],
                            'sheet_name':json_data["sheet_name"],
                            },
                            {
                            '$set' :
                            {
                                'attributes' : attributes_data,
                                'updated_at' : datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')  
                            }
                    })
                except Exception as ex:
                    print(ex.message)
                return {"status": True, "message":"attributes updated successfully"}
        else:
            return {'status':False, 'message':'Not a valid user'}