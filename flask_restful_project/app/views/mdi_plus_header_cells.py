from flask_restful import Resource
from flask import request
from app import mongo
import bson
from bson.json_util import dumps
import json
from datetime import datetime

class Headercells(Resource):
    def get(self):
        user_id = request.headers.get('id')
        grid_id= request.headers.get('grid_id')
        cell_id= request.headers.get('cell_id')
        sheet_name = request.headers.get('sheet_name')
        header_type = request.headers.get('header_type')
        user_object_id = bson.ObjectId(user_id)
        user = mongo.db.mdi_plus_users.find_one({'_id': user_object_id })
        if user is not None:
            entry = mongo.db.mdi_plus_data_grid.find_one({"grid_id":grid_id})
            if entry is not None:
               sheets = entry['sheets']
               for s in sheets:
                   if s['sheet_name'] == sheet_name:
                        if header_type == 'comparator':
                           head_cells = s['comparator_header_cells']
                        elif header_type == 'preference':
                            head_cells = s['preference_header_cells']
                        return {'status': True, 'data': dumps(head_cells)}
            else:
                return {'status':False, 'data':dumps({})}
        else:
            return {'status':False, 'data':dumps({})}
    
    def post(sellf):
        user_id = request.headers.get('id')
        grid_id= request.headers.get('grid_id')
        sheet_name = request.headers.get('sheet_name')
        header_type = request.headers.get('header_type')
        json_data = request.get_json(force=True)
        print('sheetname',sheet_name)
        user_object_id = bson.ObjectId(user_id)
        user = mongo.db.mdi_plus_users.find_one({'_id': user_object_id })
        if user is not None:
            entry = mongo.db.mdi_plus_data_grid.find_one({"grid_id":grid_id})
            if entry is not None:
                sheet_check = mongo.db.mdi_plus_data_grid.find_one({"grid_id":grid_id, "sheets": {"$elemMatch":{"sheet_name": sheet_name}}})
                if sheet_check is not None:
                    matched_sheet = []
                    for s in sheet_check['sheets']:
                        if s['sheet_name'] == sheet_name:
                            matched_sheet.append(s)
                    sheet_index = sheet_check['sheets'].index(matched_sheet[0])
                    ms = sheet_check['sheets'][sheet_index]
                    #print('matched_sheet', ms)
                    if header_type == 'comparator':
                        matched_head_list = ms['comparator_header_cells'] 
                        #cell_check = mongo.db.mdi_plus_data_grid.find_one({"grid_id":grid_id, "sheets.sheet_name": sheet_name, "sheets.comparator_header_cells.cell_id": json_data['cell_id']})
                        cell_check = mongo.db.mdi_plus_data_grid.find_one({"grid_id":grid_id, "sheets": {"$elemMatch":{"sheet_name": sheet_name,"comparator_header_cells":{"$elemMatch":{"cell_id": json_data['cell_id']}}}}})
                        print('cell_check', cell_check)
                    elif header_type == 'preference':
                        print('am in preference')
                        matched_head_list = ms['preference_header_cells'] 
                        #cell_check = mongo.db.mdi_plus_data_grid.find_one({"grid_id":grid_id, "sheets.sheet_name": sheet_name, "sheets.preference_header_cells.cell_id": json_data['cell_id']})
                        cell_check = mongo.db.mdi_plus_data_grid.find_one({"grid_id":grid_id, "sheets": {"$elemMatch":{"sheet_name": sheet_name,"preference_header_cells":{"$elemMatch":{"cell_id": json_data['cell_id']}}}}})
                        print('cell_check', cell_check)
                    if cell_check is None:
                        notes_list = []
                        notes_list.append(json_data["notes"])
                        json_data['notes'] = notes_list
                        matched_head_list.append(json_data)
                        sheet_check['sheets'][sheet_check['sheets'].index(ms)] = ms
                        mongo.db.mdi_plus_data_grid.update_one(
                        {
                        'grid_id' : grid_id
                        },
                        {
                        '$set' :
                        {
                            'sheets' : sheet_check['sheets'],
                            'updated_at' : datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')  
                        }
                        })
                        return {'status':True, 'message':'saved successfully'}
                    else:
                        print('am in nextr elseeeeeeee')
                        cell_list = []
                        print('matched_head_list', matched_head_list)
                        for c in matched_head_list:
                            if c['cell_id'] == json_data['cell_id']:
                                cell_list.append(c)
                        print('cell_list', matched_head_list)
                        cell_index = matched_head_list.index(cell_list[0])
                        mc = matched_head_list[cell_index]
                        #print(mc)
                        print(json_data["notes"])
                        mc['notes'].append(json_data["notes"])
                        print( mc['notes'])
                        json_data['notes'] = mc['notes']
                        matched_head_list[cell_index] = json_data
                        #print(matched_head_list)
                        sheet_check['sheets'][sheet_check['sheets'].index(ms)] = ms
                        mongo.db.mdi_plus_data_grid.update_one(
                        {
                        'grid_id' : grid_id
                        },
                        {
                        '$set' :
                        {
                            'sheets' : sheet_check['sheets'],
                            'updated_at' : datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')  
                        }
                        })
                        return {'status':True, 'message':'updated successfully'}
                else:
                    sd = {}
                    sd['sheet_name'] = sheet_name
                    sd['attribute_cells'] = []
                    sd['preference_cells'] = []
                    sd['comparator_cells'] = []
                    notes_list = []
                    notes_list.append(json_data["notes"])
                    json_data['notes'] = notes_list
                    data = []
                    data.append(json_data)
                    if header_type == 'comparator':
                        sd['comparator_header_cells'] = data
                        sd['preference_header_cells'] = []
                    elif header_type == 'preference':
                        sd['preference_header_cells'] = data
                        sd['comparator_header_cells'] = []
                    entry['sheets'].append(sd)
                    mongo.db.mdi_plus_data_grid.update_one(
                        {
                        'grid_id' : grid_id
                        },
                        {
                        '$set' :
                        {
                            'sheets' : entry['sheets'],
                            'updated_at' : datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')  
                        }
                    })
                    return {'status':True, 'message':'saved successfully'}
            else:
                sheet_data = []
                sd = {}
                sd['sheet_name'] = sheet_name
                sd['attribute_cells'] = []
                sd['preference_cells'] = []
                sd['comparator_cells'] = []
                notes_list = []
                notes_list.append(json_data["notes"])
                json_data['notes'] = notes_list
                data = []
                data.append(json_data)
                if header_type == 'comparator':
                    sd['comparator_header_cells'] = data
                    sd['preference_header_cells'] = []
                elif header_type == 'preference':
                    sd['preference_header_cells'] = data
                    sd['comparator_header_cells'] = []
                sheet_data.append(sd)
                mongo.db.mdi_plus_data_grid.insert(
                    {
                        'grid_id' : grid_id,
                        'sheets': sheet_data,
                        "created_at" :datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f'),
                        "updated_at" :datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')            
                    }
                )
                return {'status':True, 'message':'saved successfully'} 
        else:
            return {'status':False, 'message':'Not a valid user'}