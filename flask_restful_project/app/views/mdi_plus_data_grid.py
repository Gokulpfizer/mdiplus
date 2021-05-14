from flask_restful import Resource
from flask import request
from app import mongo
import bson
from bson.json_util import dumps
import json
from datetime import datetime


class DataGrid(Resource):

    def findSheet(arr , sheet_name):
        for x in arr:
            if x["sheet_name"] == sheet_name:
                return x

    def findcamparator(arr , sheet_name, cellinfo):
        attributecellsfinal=[]
        print("========")
        for x in arr:
            if x["sheet_name"] == sheet_name:
                attributecells=x["camparator_cells"]
                if len(attributecells) == 0:
                    x["camparator_cells"]=cellinfo
                else:
                    for newcells in cellinfo:
                        print("newcells========")
                        print(newcells)
                        for oldcells in attributecells:
                            print("oldcells========")
                            print(oldcells)
                            if(newcells["column_index"] != oldcells["column_index"]):
                                x["camparator_cells"].append(newcells)

        return arr
    def post(self):
        print('am here')
        _json = request.get_json(force=True)
        print(_json)
        data_grid_id = str(_json['data_grid_id'])
        sheet_name = str(_json['sheet_name'])
        sheet_index = int(_json['sheet_index'])
        dataGridData=mongo.db.mdi_plus_data_grid.find_one({'_id':  bson.ObjectId(data_grid_id)})
        print(dataGridData)
        if dataGridData is not None:
            return {"sheet": dataGridData["sheets"]}
        else:
            return {"sheet": []}

        # for x in dataGridData["sheets"]:
        #     if x["sheet_name"] == sheet_name:
        #         sheetfound=x

    
    def put(self):
        print('am here')
        _json = request.get_json(force=True)
        print(_json)
        data_grid_id = str(_json['data_grid_id'])
        sheet_index = int(_json['sheet_index'])
        sheet_data=_json['sheet_data']
        dataGridData=json.loads(dumps(mongo.db.mdi_plus_data_grid.find_one({'_id':  bson.ObjectId(data_grid_id)}) ))
        print(dataGridData)
        for x in dataGridData["sheets"]:
            if x["sheet_index"] == sheet_index:
                x=sheet_data
        
        mongo.db.mdi_plus_data_grid.update({'_id': bson.ObjectId(data_grid_id)  },{"$set": {"sheets": dataGridData["sheets"] } })
        return "sheets updated"

class DataGridUpdate(Resource):
    def post(self):
        print('am heredfffffffff')
        _json = request.get_json(force=True)
        print(_json)
        data_grid_id = str(_json['data_grid_id'])
        sheet_index = int(_json['sheet_index'])
        sheet_data= _json['sheet_data']
        dataGridData=json.loads(dumps(mongo.db.mdi_plus_data_grid.find_one({'_id':  bson.ObjectId(data_grid_id)}) ))
        print(dataGridData)
        _sheets=[]
        for x in dataGridData["sheets"]:
            if x["sheet_index"] == sheet_index:
                _sheets.append(sheet_data)
            else:
                _sheets.append(x)
        
        mongo.db.mdi_plus_data_grid.update({'_id': bson.ObjectId(data_grid_id)  },{"$set": {"sheets": _sheets } })
        return "sheets updated"
