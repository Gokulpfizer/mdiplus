from flask_restful import Resource
from flask import request
from app import mongo
import bson
from bson.json_util import dumps
import json
from datetime import datetime

def findPreferences(arr , sheet_name, cellinfo):
    attributecellsfinal=[]
    print("========")
    for x in arr:
        if x["sheet_name"] == sheet_name:
            attributecells=x["preference_cells"]
            if len(attributecells) == 0:
                x["preference_cells"]=cellinfo
            else:
                 for newcells in cellinfo:
                    print("newcells========")
                    print(newcells)
                    for oldcells in attributecells:
                        print("oldcells========")
                        print(oldcells)
                        if(newcells["column_index"] != oldcells["column_index"]):
                            x["preference_cells"].append(newcells)

    return arr

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

class DataGridPreferences(Resource):
    def post(self):
        _json = request.json
        print(_json)
        data_grid_id = str(_json['data_grid_id'])
        sheet_name = str(_json['sheet_name'])
        cellinfo=_json["cell_info"]
        print("data_grid_id prefrences")
        dataGridData=mongo.db.mdi_plus_data_grid.find_one({'_id': bson.ObjectId(data_grid_id), "sheets.sheet_name": sheet_name})
        print(dataGridData)
        camparatorsunique=findPreferences(dataGridData["sheets"] , sheet_name, cellinfo)
        mongo.db.mdi_plus_data_grid.update({'_id': bson.ObjectId(data_grid_id)  },{"$set": {"sheets": camparatorsunique} })
        print(camparatorsunique)
        return "dataGridData"
        
class DataGridComporators(Resource):

    def post(self):
        _json = request.json
        print(_json)
        data_grid_id = str(_json['data_grid_id'])
        sheet_name = str(_json['sheet_name'])
        cellinfo=_json["cell_info"]
        print(data_grid_id)
        dataGridData=mongo.db.mdi_plus_data_grid.find_one({'_id': bson.ObjectId(data_grid_id), "sheets.sheet_name": sheet_name})
        print(dataGridData)
        camparatorsunique=findcamparator(dataGridData["sheets"] , sheet_name, cellinfo)
        mongo.db.mdi_plus_data_grid.update({'_id': bson.ObjectId(data_grid_id)  },{"$set": {"sheets": camparatorsunique} })
        print(camparatorsunique)
        return "dataGridData"

class DataGridAttributes(Resource):

    def post(self):
        try:
            _json = request.json
            print(_json)
            data_grid_id = str(_json['data_grid_id'])
            sheet_name = str(_json['sheet_name'])
            sheet_index=int(_json['sheet_index'])
            dataGridData=mongo.db.mdi_plus_data_grid.find_one({'_id': bson.ObjectId(data_grid_id)})
            print(dataGridData)
            print("--------------")
            print(len(dataGridData["sheets"]))
            if len(dataGridData["sheets"]) < sheet_index:
                sheet_index = sheet_index-1
                headersdata= json.loads(dumps(mongo.db.mdi_plus_attributes.find({"attributes_type":"attribute"})))
                attributes=[]
                i=0
                for element in headersdata:
                    eachobject={
                        "column_index": i,
                        "name": element["attributes_name"]
                    }
                    i+=1
                    attributes.append(eachobject)
                newsheet ={
                        "sheet_name" : sheet_name,
                        "sheet_index" : sheet_index,
                        "attribute_cells" :attributes,
                        "camparator_cells" : [],
                        "preference_cells" : [ ]
                    }
                dataGridData["sheets"].append(newsheet)
                mongo.db.mdi_plus_data_grid.update({'_id': bson.ObjectId(data_grid_id)  },{"$set": {"sheets": dataGridData["sheets"] } })
                
            return "dataGridData"
        except Exception as ex:
            print(ex.message)
            return "not inserted"

class Comporators(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        comporators = json_data["data"]
        uid = request.headers.get('id')
        grid_id= request.headers.get('grid_id')
        #cell_id= request.headers.get('cell_id')
        sheet_name = request.headers.get('sheet_name')
        user_object_id = bson.ObjectId(uid)
        user = mongo.db.mdi_plus_users.find_one({'_id': user_object_id })
        if user is not None:
            print(comporators)
            if len(comporators) != 0:
                for comp in comporators:
                    comparator_count=mongo.db.mdi_plus_attributes.count({"attributes_type":"comparator","grid_id":grid_id,"cell_id":comp["cell_id"], "sheet_name":sheet_name})
                    print('comparator_count',comparator_count)
                    if comparator_count == 0:
                        insert_comparator= {"attributes_name":comp['name'],"attributes_type":"comparator","grid_id":grid_id,"cell_id":comp["cell_id"], "sheet_name":sheet_name,"created_at" : datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S'),"updated_at":datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')}
                        mongo.db.mdi_plus_attributes.insert(insert_comparator)
                        message = 'Comparator saved successfully'
                    else:
                        print('am in elseeeeeeeeeeeeeeeeesssss')
                        print('comp_name', comp['name'])
                        try:
                            mongo.db.mdi_plus_attributes.update_one(
                                {
                                "attributes_type":"comparator",
                                "grid_id":grid_id,
                                "cell_id":comp["cell_id"],
                                "sheet_name":sheet_name
                                },
                                {
                                '$set' :
                                {
                                    "attributes_name":comp['name'],
                                    'updated_at' : datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')  
                                }
                            })
                            message = 'Comparator updated successfully'
                        except Exception as ex:
                            print(ex.message)
                return {"status":True, "message":message}
            else:
                return {"status":False, "message":"Comparator list is empty"}
        else:
            return {'status':False, 'message':'Not a valid user'}

class Preferences(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        preferences = json_data["data"]
        grid_id= request.headers.get('grid_id')
        #cell_id= request.headers.get('cell_id')
        sheet_name = request.headers.get('sheet_name')
        uid = request.headers.get('id')
        user_object_id = bson.ObjectId(uid)
        user = mongo.db.mdi_plus_users.find_one({'_id': user_object_id })
        if user is not None:
            if len(preferences) != 0:
                for pref in preferences:
                    preference_count=mongo.db.mdi_plus_attributes.count({"attributes_type":"preference","grid_id":grid_id,"cell_id":pref["cell_id"], "sheet_name":sheet_name})
                    print(preference_count)
                    if preference_count == 0:
                        insert_preference= {"attributes_name":pref['name'],"attributes_type":"preference","grid_id":grid_id,"cell_id":pref["cell_id"], "sheet_name":sheet_name,"created_at" : datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S'),"updated_at":datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')}
                        mongo.db.mdi_plus_attributes.insert(insert_preference)
                        message = 'Prefernece saved successfully'
                    else:
                        print('am in else')
                        mongo.db.mdi_plus_attributes.update_one(
                            {
                            "attributes_type":"preference",
                            "grid_id":grid_id,
                            "cell_id":pref["cell_id"],
                            "sheet_name":sheet_name
                            },
                            {
                            '$set' :
                            {
                                "attributes_name":pref['name'],
                                'updated_at' : datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')  
                            }
                        })
                        message = 'Prefernece updated successfully'
                return {"status":True, "message":message}
            else:
                return {"status":False, "message":"Prefernece list is empty"}
        else:
            return {'status':False, 'message':'Not a valid user'}

class Attributes(Resource):
    def get(self):
        uid = request.headers.get('id')
        user_object_id = bson.ObjectId(uid)
        user = mongo.db.mdi_plus_users.find_one({'_id': user_object_id })
        if user is not None:
            attr_count = mongo.db.mdi_plus_attributes.count({"attributes_type":"attribute"})
            if attr_count>0:
                attr_entries=mongo.db.mdi_plus_attributes.find({"attributes_type":"attribute"})
                atttributes = []
                for attr in attr_entries:
                    atttributes.append(attr['attributes_name'])
                return {"status":True, "data":atttributes}
            else:
                return {"status":True, "data":[]}
        else:
            return {"status":True, "data":[]}

class AttributeType(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        grid_id= request.headers.get('grid_id')
        cell_id= request.headers.get('cell_id')
        sheet_name = request.headers.get('sheet_name')
        attr_name = json_data['attribute_name']
        uid = request.headers.get('id')
        user_object_id = bson.ObjectId(uid)
        user = mongo.db.mdi_plus_users.find_one({'_id': user_object_id })
        if user is not None:
            #print('am here')
            print(grid_id)
            print(cell_id)
            print(sheet_name)
            atttributes = mongo.db.mdi_plus_attributes.find_one({"attributes_name":attr_name,"grid_id":grid_id,"cell_id":cell_id, "sheet_name":sheet_name})
            if atttributes is None:
                print('am here')
                attr_entries=mongo.db.mdi_plus_attributes.find_one({"attributes_name":attr_name,"attributes_type":"attribute"})
                if attr_entries is not None:
                    print('attr_type',attr_entries["attributes_type"])
                    return {"status":True, "Type":attr_entries["attributes_type"]}
                else:
                    return {"status":True, "Type":""}
            else:
                #print('am here again') 
                return {"status":True, "Type":atttributes["attributes_type"]}
        else:
            return {"status":True, "Type":""}
    def get(self):
        grid_id= request.headers.get('grid_id')
        cell_id= request.headers.get('cell_id')
        sheet_name = request.headers.get('sheet_name')
        attr_name = request.headers.get('attribute_name')
        uid = request.headers.get('id')
        user_object_id = bson.ObjectId(uid)
        user = mongo.db.mdi_plus_users.find_one({'_id': user_object_id })
        if user is not None:
            #print('am here')
            print(grid_id)
            print(cell_id)
            print(sheet_name)
            atttributes = mongo.db.mdi_plus_attributes.find_one({"attributes_name":attr_name,"grid_id":grid_id,"cell_id":cell_id, "sheet_name":sheet_name})
            if atttributes is None:
                print('am here')
                attr_entries=mongo.db.mdi_plus_attributes.find_one({"attributes_name":attr_name,"attributes_type":"attribute"})
                if attr_entries is not None:
                    print(attr_entries["attributes_type"])
                    return {"status":True, "Type":attr_entries["attributes_type"]}
                else:
                    return {"status":True, "Type":""}
            else:
                #print('am here again') 
                return {"status":True, "Type":atttributes["attributes_type"]}
        else:
            return {"status":True, "Type":""}