from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import secrets
from datetime import datetime 
import pymongo
from pymongo import MongoClient
from bson import json_util

import json

app = Flask(__name__)
api = Api(app)


# Make a connection to Mongo server
client = MongoClient('localhost', 27017)

# initialize db instance 
db = client["Users"]

# see all collections present in this db
user_collection = db['users']

# Insert a document
# document = {"name": "david", "phone": 1245373748}
#response = user_collection.insert_one(document)
#print(response.inserted_id)


# DATA = {1:{"expire": "1427736345","user":"Shivam Patel"}}
# user_collection.insert_one(DATA)
DATA = {}

data_post_args = reqparse.RequestParser()
data_post_args.add_argument('expire', type=str, required=False,default = int(datetime.now().timestamp())+30*86400, help="Expiry is required.")
data_post_args.add_argument('user', type=str, required=True, help="user is required.")

data_put_args = reqparse.RequestParser()
data_put_args.add_argument('expire', type=str)
data_put_args.add_argument('user', type=str)
import pprint

def parse_json(data):
	return json.loads(json_util.dumps(data))

xs = user_collection.find_one({'expire':1427736345})
pprint.pprint(xs)


class Data(Resource):

	def get(self, data_id):
		out = DATA[data_id].copy()
		out["guid"] = data_id
		return [val for val in user_collection.find()]

	def post(self,data_id=secrets.token_hex(15)):
		args = data_post_args.parse_args()
		# if data_id in DATA:
			# abort(409, "User's data already present.")
		DATA[data_id] = {'_id':data_id,"expire": args["expire"], "user": args["user"]}
		out = DATA[data_id].copy()
		out["guid"] = user_collection.insert_one(parse_json(out)).inserted_id
		# record = json.dumps(DATA[data_id])
		response = user_collection.insert_one(parse_json(out))
		
		return out

	def delete(self, data_id):
		del DATA[data_id]
		# print(user_collection.find_one({'guid':data_id}))
		response = user_collection.delete_one({'_id':data_id})
		return DATA

	def put(self, data_id):
		args = data_put_args.parse_args()
		# Updating fan quantity form 10 to 25.
		
		
		if data_id not in DATA:
			abort(404, message="Data doen't exist, can't update.")
		if args['user']:
			DATA[data_id]['user'] = args['user']
			filter = { '_id': data_id }
			newvalues = { "$set": { 'user': args['user']} }
			user_collection.update_one(filter, newvalues)
		if args['expire']:
			DATA[data_id]['expire'] = args['expire']
			filter = { '_id': data_id }
			newvalues = { "$set": {'expire':args['expire'] }}
			user_collection.update_one(filter, newvalues)
			return DATA[data_id]

class DataList(Resource):
	def get(self):
		out = DATA.copy()
		guid_out = []
		for key,val in out.items():
			val['guid'] = key
			guid_out.append(val)
		return guid_out

api.add_resource(DataList,'/data')
api.add_resource(Data,'/data/<data_id>','/data')


if __name__ == '__main__':
    app.run(debug=True)

'''
 import secrets
>>> secrets.token_hex(15)
'8d9bad5b43259c6ee27d9aadc7b832'
>>> secrets.token_urlsafe(22)   # may include '_-' unclear if that is acceptable
'teRq7IqhaRU0S3euX1ji9f58WzUkrg'
'''