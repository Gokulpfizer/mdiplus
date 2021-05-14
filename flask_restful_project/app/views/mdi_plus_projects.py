from flask_restful import Resource
from flask import request
from app import mongo
import bson
from bson.json_util import dumps
import json
from datetime import datetime

class ProjectsList(Resource):
    def get(self):
        oid = request.headers.get('id')
        indication = request.headers.get('indication')
        if oid:
            object_id = bson.ObjectId(oid)
            user = mongo.db.mdi_plus_users.find_one({'_id': object_id })
            if user is not None:
                find_entries = json.loads(dumps(mongo.db.mdi_plus_projects.find({'user_id': oid})))
                #find_entries = json.loads(dumps(mongo.db.mdi_plus_projects.find()))
                indication = []
                sheets=[]
                for entry in find_entries:
                    print(str(entry['_id']["$oid"]))
                    indication.append(entry['indication'])
                    datagrid_data=mongo.db.mdi_plus_data_grid.find_one({"project_id":  str(entry['_id']["$oid"])})
                    print("datagrid")
                    print(datagrid_data)
                    sheetinfo ={}
                    projectandsheet=[]
                    if datagrid_data is not None:
                        for sheet in datagrid_data['sheets']:
                            projectandsheet.append(sheet['sheet_name'])
                        sheetinfo['sheets']=projectandsheet
                        sheetinfo['project_id']=str(entry['_id']["$oid"])
                        sheetinfo['id']=entry['indication']
                        sheets.append(sheetinfo)
                        
                return {'status':True, 'data':indication, 'sheets': sheets}
            else:
                return {'status':False, 'data':[]}
        if indication:
            find_entries = json.loads(dumps(mongo.db.mdi_plus_projects.find({'indication': indication})))
                #find_entries = json.loads(dumps(mongo.db.mdi_plus_projects.find()))
            projects = []
            for entry in find_entries:
                    print(str(entry['_id']["$oid"]))
                    datagrid_data=mongo.db.mdi_plus_data_grid.find_one({"project_id":  str(entry['_id']["$oid"])})
                    print("datagrid")
                    print(datagrid_data)
                    if datagrid_data is not None:
                        entry["data_grid_id"]= str(datagrid_data['_id'])
                        projects.append(entry)
                    
            return {'status':True, 'data':projects}     
        else:
            return {'status':False, 'data':[]}

    def post(self):
        json_data = request.get_json(force=True)
        oid = request.headers.get('id')
        indication = request.headers.get('indication')
        if oid:
            object_id = bson.ObjectId(oid)
            user = mongo.db.mdi_plus_users.find_one({'_id': object_id })
            if user is not None:
                find_entries = json.loads(dumps(mongo.db.mdi_plus_projects.find({'user_id': oid})))
                #find_entries = json.loads(dumps(mongo.db.mdi_plus_projects.find()))
                projects = []
                for entry in find_entries:
                    projects.append(entry['indication'])
                print(projects)
                return {'status':True, 'data':projects}
            else:
                return {'status':False, 'data':[]}
        if indication:
            find_entries = json.loads(dumps(mongo.db.mdi_plus_projects.find({'indication': indication})))
                #find_entries = json.loads(dumps(mongo.db.mdi_plus_projects.find()))
            projects = []
            for entry in find_entries:
                    print(str(entry['_id']["$oid"]))
                    _project_id=str(entry['_id']["$oid"])
                    datagrid_data=mongo.db.mdi_plus_data_grid.find_one({"project_id":  str(entry['_id']["$oid"])})
                    print("datagrid")
                    print(datagrid_data)
                    
                    if datagrid_data is not None:
                        entry["data_grid_id"]= str(datagrid_data['_id'])
                        _new_sheet_name=json_data['new_sheet_name']
                        _old_project_id=json_data['old_project_id']
                        _row_id=json_data['row_id']
                        _column_id=json_data['column_id']
                        _old_grid_id=json_data['old_grid_id']
                        _new_sheet_cells=json_data['new_sheet_cells']
                        mongo.db.mdi_plus_copy_history.insert(json_data)
                        newsheetindex=0
                        for cellid in json_data['cell_ids']:
                            print(cellid)
                            cellinfo=mongo.db.mdi_plus_cell.find_one({"cell_id": cellid,"project_id": _old_project_id, "data_grid_id": _old_grid_id  })
                            print("--------------cellinfo old")
                            print(cellinfo)
                            if cellinfo is not None:
                                del cellinfo['_id']
                                cellinfo['row_id']=_row_id
                                cellinfo['sheet_name']=_new_sheet_name
                                cellinfo['project_id']=_project_id
                                cellinfo['data_grid_id']= str(datagrid_data['_id'])
                                cellinfo['column_id']=_column_id
                                cellinfo['cell_id']=_new_sheet_cells[newsheetindex]
                                print("--------------cellinfo new")
                                print(cellinfo)
                                mongo.db.mdi_plus_cell.insert(cellinfo)
                            _column_id= _column_id+1
                            newsheetindex=newsheetindex+1
                        projects.append(entry)
                    
            return {'status':True, 'data':projects}     
        else:
            return {'status':False, 'data':[]}

class Projects(Resource):
    def get(self):
        oid = request.headers.get('id')
        if oid:
            object_id = bson.ObjectId(oid)
            user = mongo.db.mdi_plus_users.find_one({'_id': object_id })
            if user is not None:
                find_entries = json.loads(dumps(mongo.db.mdi_plus_projects.find({'user_id': oid})))
                #find_entries = json.loads(dumps(mongo.db.mdi_plus_projects.find()))
                projects = []
                for entry in find_entries:
                    print(str(entry['_id']["$oid"]))
                    datagrid_data=mongo.db.mdi_plus_data_grid.find_one({"project_id":  str(entry['_id']["$oid"])})
                    print("datagrid")
                    print(datagrid_data)
                    if datagrid_data is not None:
                        entry["data_grid_id"]= str(datagrid_data['_id'])
                    for c in entry["collaborators"]:
                        if entry['user_id'] == oid or c['collaborator'] == user['username']:
                            if not entry in projects:
                                projects.append(entry)
                print(projects)
                return {'status':True, 'data':projects}
            else:
                return {'status':False, 'data':[]}
        else:
            return {'status':False, 'data':[]}
            
    def post(self):
        print('am here')
        json_data = request.get_json(force=True)
        object_id = bson.ObjectId(json_data["id"])
        #indication = json_data["indication"]+"_"+json_data["compound_number"]
        user = mongo.db.mdi_plus_users.find_one({'_id': object_id })
        if user is not None:
            project_details = mongo.db.mdi_plus_projects.find_one({'user_id':json_data["id"], 'indication': json_data["indication"]})
            if project_details is None:
                if len(json_data["collaborators"])>0:
                    project = {
                        "user_id":json_data["id"],
                        "project_owner":user["username"],
                        "indication":json_data["indication"],
                        "compound_number":json_data["compound_number"],
                        "collaborators":json_data["collaborators"],
                        "created_at" :datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f'),
                        "updated_at" :datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f'),
                    }
                    project_insert = mongo.db.mdi_plus_projects.insert(project)
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
                    datagrid= {
                        "project_id": str(project_insert),
                        "sheets": [
                                {
                                    "sheet_name" : "Sheet1",
                                    "sheet_index" : 0,
                                    "attribute_cells" :attributes,
                                    "camparator_cells" : [
                                    ],
                                    "preference_cells" : [ ]
                                }
                            ]
                    }
                    datagrid_insert = mongo.db.mdi_plus_data_grid.insert(datagrid)
                    return {'status': True,'message':'Project created successfully'}
                else:
                    return {'status': True, 'message':'need collabarators'}
            else:
                return {'status': False,'message':'Project is already existed'}
        else:
            return {'status':False, 'message':'Not a valid user'}

class ProjectAccess(Resource):
    def get(self):
        uid = request.headers.get('id')
        project_id = request.headers.get('project_id')
        user_object_id = bson.ObjectId(uid)
        user = mongo.db.mdi_plus_users.find_one({'_id': user_object_id })
        if user is not None:
            project_details = mongo.db.mdi_plus_projects.find_one({'_id': bson.ObjectId(project_id)})
            if project_details['project_owner'] == user["username"]:
                return {"status":True, "access": "Read and Write"}
            else:
                collaborators = []
                for c in project_details["collaborators"]:
                    if c['collaborator'] == user["username"]:
                        return {"status":True, "access": c["permission"]}
        else:
            return {'status':False, 'message':'Not a valid user'}


