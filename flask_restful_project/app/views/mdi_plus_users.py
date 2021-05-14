from flask_restful import Resource
#from main import app
from flask import request
from app import mongo
import json
import bson
from bson.json_util import dumps
from flask import render_template, make_response

class Login(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        user_name = json_data['user_name'].title()
        print(user_name)
        password = json_data['password']
        user = mongo.db.mdi_plus_users.find_one({'username': user_name })
        
        if user is not None:
            user_password = mongo.db.mdi_plus_users.find_one({'username': user_name, "password": password })
            if user_password is not None:
                return {'status': True, 'message':'Username is existed', 'token': str(user['_id']), 'username':user['username']}
            else:
                return {'status': False, 'message':'Password is wrong', 'token':'', 'username':''}
        else:
            return {'status': False, 'message':'Username is wrong', 'token':'', 'username':''}

class Users(Resource):
    def get(self):
        object_id = request.headers.get('id')
        if object_id:
            user = mongo.db.mdi_plus_users.find_one({'_id': bson.ObjectId(object_id)})
            if user is not None:
                #print(user)
                find_entries = mongo.db.mdi_plus_users.find()
                users = []
                for d in find_entries:
                    users.append(d['username'])
                users.remove(user['username'])
                return {'status':True, 'data':users}
        else:
            return {'status':True, 'data':[]}

class AppointmentController(Resource):
    def get(self):
        args=request.args
        #print(args["id"])
        object_id = bson.ObjectId(args["id"])
        #print(object_id)
        user = mongo.db.mdi_plus_users.find_one({'_id': object_id })
        #print(user)
        if user is not None:
            return {"data":"http://127.0.0.1:5000/home?id="+args["id"]+'&project_name='+args["project_name"]}
        else:
            return {"data":"http://127.0.0.1:5000/home"}