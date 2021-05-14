from flask_restful import Resource
from flask import request
from app import mongo
import bson
from bson.json_util import dumps
import json
from datetime import datetime

class Measures(Resource):
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
                measures = entry['measures']
                d={}
                for m in measures:
                    d[m['measure_name']] = m['measure_value']
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
            Measures = mongo.db.mdi_plus_cell.find_one({"data_grid_id":json_data['grid_id'], "cell_id":json_data["cell_id"], "sheet_name":json_data["sheet_name"]})
            print("--------")
            print(Measures)
            if Measures is None:
                notes_list = []
                notes_list.append(json_data["notes"])
                measures_data =[]
                for m in ['mean_clinical_effect_estimate','lower_95_ci','upper_95_ci','sample_size_n','standard_error','distribution',\
                        'source_document','mean_and_95_ci_for_reporting','mean_and_standard_error_for_reporting', 'notes','qc_status','description']:
                    if m == 'notes':
                        d = {}
                        d['measure_name'] = m
                        d['measure_value'] = notes_list
                        measures_data.append(d)
                    elif m == 'mean_and_95_ci_for_reporting':
                        d = {}
                        d['measure_name'] = m
                        d['measure_value'] = json_data['mean_clinical_effect_estimate']+" [95% CI = ("+json_data["lower_95_ci"]+","+json_data["upper_95_ci"]+")]"
                        measures_data.append(d)
                    elif m == 'mean_and_standard_error_for_reporting':
                        d = {}
                        d['measure_name'] = m
                        d['measure_value'] = json_data['mean_clinical_effect_estimate']+" [SE = "+json_data["standard_error"]+"]"
                        measures_data.append(d)
                    else:
                        d = {}
                        d['measure_name'] = m
                        d['measure_value'] = json_data[m]
                        measures_data.append(d)
                
                _cellCount = mongo.db.mdi_plus_cell.count({'data_grid_id' : json_data['grid_id'],'sheet_name':json_data["sheet_name"],'cell_id':json_data["cell_id"]})
                print(_cellCount)
                if _cellCount == 0:
                    mongo.db.mdi_plus_cell.insert(
                        {
                            'data_grid_id' : json_data['grid_id'],
                            'project_id' : json_data['project_id'],
                            'cell_id':json_data["cell_id"],
                            'sheet_name':json_data["sheet_name"],
                            'camparator_header':json_data["attribute_name"],
                            'row_attribute_value':json_data["row_attribute_value"],
                            'measures': measures_data,
                            "created_at" :datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f'),
                            "updated_at" :datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')            
                        }
                    )
                else:
                    mongo.db.mdi_plus_cell.update({'data_grid_id' : json_data['grid_id'],'sheet_name':json_data["sheet_name"],'cell_id':json_data["cell_id"]} ,{"$set": {'camparator_header':json_data["attribute_name"],'row_attribute_value':json_data["row_attribute_value"],'measures': measures_data,"updated_at" :datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f') } })
                return {"status": True, "message":"Measures saved successfully"}
            else:
                notes_list = []
                if "measures" in Measures:
                    for ms in Measures['measures']:
                        if ms['measure_name'] == 'notes':
                            #ms['measure_value'].append(json_data["notes"])
                            notes_list.append(ms['measure_value'])
                    #Measures["notes"].append(json_data["notes"])
                    notes_list[0].append(json_data["notes"])
                else:
                    notes_list.append(json_data["notes"])
                measures_data =[]
                for m in ['mean_clinical_effect_estimate','lower_95_ci','upper_95_ci','sample_size_n','standard_error','distribution',\
                        'source_document','mean_and_95_ci_for_reporting','mean_and_standard_error_for_reporting', 'notes', 'qc_status','description']:
                    if m == 'notes':
                        d = {}
                        d['measure_name'] = m
                        if "measures" in Measures:
                            d['measure_value'] = notes_list[0]
                        else:
                            d['measure_value'] = notes_list
                        measures_data.append(d)
                    elif m == 'mean_and_95_ci_for_reporting':
                        d = {}
                        d['measure_name'] = m
                        d['measure_value'] = json_data['mean_clinical_effect_estimate']+" [95% CI = ("+json_data["lower_95_ci"]+","+json_data["upper_95_ci"]+")]"
                        measures_data.append(d)
                    elif m == 'mean_and_standard_error_for_reporting':
                        d = {}
                        d['measure_name'] = m
                        d['measure_value'] = json_data['mean_clinical_effect_estimate']+" [SE = "+json_data["standard_error"]+"]"
                        measures_data.append(d)
                    else:
                        d = {}
                        d['measure_name'] = m
                        d['measure_value'] = json_data[m]
                        measures_data.append(d)
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
                                'measures' : measures_data,
                                'updated_at' : datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S.%f')  
                            }
                    })
                except Exception as ex:
                    print(ex.message)
                return {"status": True, "message":"Measures updated successfully"}
        else:
            return {'status':False, 'message':'Not a valid user'}


class SourceDocuments(Resource):
    def get(self):
        user_id = request.headers.get('id')
        user_object_id = bson.ObjectId(user_id)
        user = mongo.db.mdi_plus_users.find_one({'_id': user_object_id })
        if user is not None:
            entry = mongo.db.mdi_plus_document_reference_names.find()
            if entry is not None:
                docs = []
                for e in entry:
                    docs.append(e["short_name"])
                return {'status':True, 'data':docs}
            else:
                return {'status':True, 'data':[]}
        else:
            return {'status':True, 'data':[]}

class ReadMeasures(Resource):
    def get(slef):
        user_id = request.headers.get('id')
        user_object_id = bson.ObjectId(user_id)
        grid_id= request.headers.get('grid_id')
        sheet_name = request.headers.get('sheet_name')
        cell_ids = request.headers.get('cell_ids').split(',')
        find_entries = mongo.db.mdi_plus_cell.find({"data_grid_id":grid_id, "sheet_name":sheet_name, "cell_id":{"$in":cell_ids}})
        if find_entries is not None:
            content = []
            for  e in find_entries:
                if 'measures' in e.keys():
                    content.append(e) 
            return {'status': True, 'rows': json.loads(dumps(content))}
        else:
            return {'status': False, "rows":[]}

def checck_attribute_type(attr_name,grid_id,sheet_name):
    atttributes = mongo.db.mdi_plus_attributes.find_one({"attributes_name":attr_name,"grid_id":grid_id,"sheet_name":sheet_name})
    if atttributes is None:
        attr_entries=mongo.db.mdi_plus_attributes.find_one({"attributes_name":attr_name,"attributes_type":"attribute"})
        if attr_entries is not None:
            return {"status":True, "Type":attr_entries["attributes_type"]}
        else:
            return {"status":True, "Type":""}
    else:
        #print('am here again') 
        return {"status":True, "Type":atttributes["attributes_type"]}

class ReadNotes(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        uid = request.headers.get('id')
        project_id = request.headers.get('project_id')
        user_object_id = bson.ObjectId(uid)
        user = mongo.db.mdi_plus_users.find_one({'_id': user_object_id })
        if user is not None:
            entry = mongo.db.mdi_plus_app_json.find_one({'project_id':project_id})
            if entry is not None:
                first_sheet = json_data['json_file']['sheets'][0]
                print('sheet', first_sheet)
                first_row = json_data['json_file']['sheets'][0]['rows'][0]['cells']
                exclude_firstrow = json_data['json_file']['sheets'][0]['rows'][1:]
                print('exclude_firstrow',exclude_firstrow)
                headers = []
                sheet_name = first_sheet['name']
                for row in first_row:
                    headers.append(row['value'])
                final_list = []
                for cell in exclude_firstrow:
                    data = {}
                    data_list = []
                    for i, j in zip(headers, cell['cells']):
                        print('iteration', i)
                        if 'cellId' in j:
                            attr_check = checck_attribute_type(i, project_id, sheet_name)
                            print('attr_type', attr_check['Type'])
                            if attr_check['Type'] == 'attribute':
                                d = {}
                                d['name'] = i
                                d['value'] = j['value']
                                if 'background' in j:
                                    d['background'] = j['background']
                                data_list.append(d)
                            elif attr_check['Type'] == 'comparator':
                                find_entries = mongo.db.mdi_plus_cell.find_one({"grid_id":project_id, "sheet_name":sheet_name, "cell_id":j["cellId"]})
                                if find_entries is not None:
                                    notes = next((n['measure_value'] for n in find_entries['measures'] if n['measure_name'] == 'notes'), None)
                                    d = {}
                                    d['name'] = i
                                    d['value'] = notes
                                    if 'background' in j:
                                        d['background'] = j['background']
                                    data_list.append(d)
                                else:
                                    d = {}
                                    d['name'] = i
                                    d['value'] = []
                                    if 'background' in j:
                                        d['background'] = j['background']
                                    data_list.append(d)
                            elif attr_check['Type'] == 'preference':
                                find_entries = mongo.db.mdi_plus_cell.find_one({"grid_id":project_id, "sheet_name":sheet_name, "cell_id":j["cellId"]})
                                print(find_entries)
                                if find_entries is not None:
                                    notes = next((n['preference_value'] for n in find_entries['preferences'] if n['preference_name'] == 'notes'), None)
                                    d = {}
                                    d['name'] = i
                                    d['value'] = notes
                                    if 'background' in j:
                                        d['background'] = j['background']
                                    data_list.append(d)
                                else:
                                    d = {}
                                    d['name'] = i
                                    d['value'] = []
                                    if 'background' in j:
                                        d['background'] = j['background']
                                    data_list.append(d)
                    data['data'] = data_list
                    final_list.append(data)
                print('final_list', final_list)
                return {'status':True, 'data':{'headers':headers, 'values': final_list}}
            else:
                return {'status':True, 'data':{}}
        else:
            return {'status':True, 'data':{}}


class Analysis(Resource):
    def post(self):
        anames_meas = {'mean_clinical_effect_estimate':'Mean','lower_95_ci':'LCI', 'upper_95_ci': 'UCI', \
        'sample_size_n': 'N', 'standard_error': 'SE', 'distribution': 'Distr', 'source_document': 'Scd', 'qc_status':'QC','description':'Desc'}
        json_data = request.get_json(force=True)
        selected_columns = json_data['selected_columns']
        uid = request.headers.get('id')
        project_id = request.headers.get('project_id')
        user_object_id = bson.ObjectId(uid)
        user = mongo.db.mdi_plus_users.find_one({'_id': user_object_id })
        if user is not None:
            entry = mongo.db.mdi_plus_app_json.find_one({'project_id':project_id})
            if entry is not None:
                first_sheet = json_data['json_file']['sheets'][0]
                #print('sheet', first_sheet)
                first_row = json_data['json_file']['sheets'][0]['rows'][0]['cells']
                exclude_firstrow = json_data['json_file']['sheets'][0]['rows'][1:]
                #print('exclude_firstrow',exclude_firstrow)
                headers = []
                sheet_name = first_sheet['name']
                for row in first_row:
                    if 'cellId' in row:
                        headers.append(row['value'])
                final_list = []
                for cell in exclude_firstrow:
                    data = {}
                    data_list = []
                    for i, j in zip(headers, cell['cells']):
                        attr_check = checck_attribute_type(i, project_id, sheet_name)
                        if 'cellId' in j:
                            if attr_check['Type'] == 'attribute':
                                d = {}
                                d['name'] = i
                                d['value'] = j['value']
                                if 'background' in j:
                                    d['background'] = j['background']
                                data_list.append(d)
                            elif attr_check['Type'] == 'comparator':
                                find_entries = mongo.db.mdi_plus_cell.find_one({"grid_id":project_id, "sheet_name":sheet_name, "cell_id":j["cellId"]})
                                if find_entries is not None:
                                    #notes = next((n['measure_value'] for n in find_entries['measures'] if n['measure_name'] == 'notes'), None)
                                    meas_data = ''
                                    for col in selected_columns:
                                        for mea in find_entries['measures']:
                                            if col == 'notes' and mea['measure_name'] == 'notes':
                                                notes_data = ''
                                                notes = next((n['measure_value'] for n in find_entries['measures'] if n['measure_name'] == 'notes'), None)
                                                for n in notes:
                                                    if notes_data == '':
                                                        notes_data = 'notes: '+n['cell_notes']
                                                    else:
                                                        notes_data = notes_data+'\n'+n['cell_notes']
                                                    #print('notes_data', notes_data)
                                                if meas_data == '':
                                                    meas_data = notes_data
                                                else:
                                                    meas_data = meas_data+'\n'+notes_data
                                            else:
                                                if mea['measure_name'] == col:
                                                    if meas_data == '':
                                                        meas_data = anames_meas[mea['measure_name']]+': '+mea['measure_value']
                                                    else:
                                                        meas_data = meas_data+'\n'+anames_meas[mea['measure_name']]+': '+mea['measure_value']
                                    d = {}
                                    d['name'] = i
                                    d['value'] = meas_data
                                    if 'background' in j:
                                        d['background'] = j['background']
                                    data_list.append(d)
                                else:
                                    d = {}
                                    d['name'] = i
                                    d['value'] = ''
                                    if 'background' in j:
                                        d['background'] = j['background']
                                    data_list.append(d)
                            elif attr_check['Type'] == 'preference':
                                '''find_entries = mongo.db.mdi_plus_cell.find_one({"grid_id":project_id, "sheet_name":sheet_name, "cell_id":j["cellId"]})
                                print('find_entries',find_entries)
                                if find_entries is not None:
                                    #notes = next((n['preference_value'] for n in find_entries['preferences'] if n['preference_name'] == 'notes'), None)
                                    pref_data = ''
                                    for col in selected_columns:
                                        for pref in find_entries['preferences']:
                                            if col == 'notes' and pref['preference_name'] == 'notes':
                                                notes_data = ''
                                                notes = next((n['preference_value'] for n in find_entries['preferences'] if n['preference_name'] == 'notes'), None)
                                                for n in notes:
                                                    if notes_data == '':
                                                        notes_data = n['cell_notes']
                                                    else:
                                                        notes_data = notes_data+'\n'+n['cell_notes']
                                                pref_data = pref_data+'\n'+notes_data
                                            else:
                                                if pref['preference_name'] == col:
                                                    if pref_data == '':
                                                        pref_data = pref['preference_value']
                                                    else:
                                                        pref_data = pref_data+'\n'+pref['preference_value']'''
                                d = {}
                                d['name'] = i
                                d['value'] = ''
                                if 'background' in j:
                                    d['background'] = j['background']
                                data_list.append(d)
                    data['data'] = data_list
                    final_list.append(data)
                print('final_list', final_list)
                return {'status':True, 'data':{'headers':headers, 'values': final_list}}
            else:
                return {'status':True, 'data':{}}
        else:
            return {'status':True, 'data':{}}

        
