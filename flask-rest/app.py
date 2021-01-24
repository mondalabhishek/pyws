from flask import Flask, request, json, Response
from pymongo import MongoClient
import logging
from logging.handlers import RotatingFileHandler
import redis


app = Flask(__name__)

redis_client = redis.Redis();

class RedisAPI(object):
    def __init__(self):
        redis_client = redis.Redis(host="localhost",port=6379, password= None)
    pass


class MongoAPI:
    def __init__(self, data) :
        app.logger.info('Instantiate DB Connection: ');
 
        self.client = MongoClient("mongodb://localhost:27017/")

        database = data ['database']
        collection = data ['collection']
        cursor = self.client[database]
        self.collection = cursor[collection]
        self.data = data

        app.logger.info('Database: '+database);
        app.logger.info('Database: '+collection);

        pass
    
    def read(self):
        app.logger.info('Read All Data from Collection');
        documents = self.collection.find()
        output = [{item: data[item] for item in data if item != '_id'} for data in documents]
        return output
    
    def write(self, data):
        app.logger.info('Writing Data');
        new_document = data['Document']
        response = self.collection.insert_one(new_document);
        output = {'Status': 'Successfully Inserted',
                    'DocumentId': str(response.inserted_id)}
        return output
    
    def update(self, data):
        app.logger.info('Updating Data');
        filt = data['Filter']
        updated_data = {"$set": data['DataToBeUpdated']}
        response = self.collection.update_one(filt, updated_data);
        output = {'Status': 'Successfully Saved' if response.modified_count>0 else 'Nothing Updated'}
        return output
    
    def delete(self,data):
        app.logger.info('Deleting Data');
        filt = data['Filter']
        response = self.collection.delete_one(filt);
        output = {'Status': 'Successfuly Deleted' if response.deleted_count>0 else 'No Document Found for deletion'}
        return output

    def getDetails(self, filter):
        app.logger.info('Getting specific Data');
        #app.logger.info("Filter: "+filter)
        
        document = self.collection.find_one(filter);
        app.logger.info(document)
        output = dict(document);
        del output['_id']
        return output

def logResponse(response, operation):
    app.logger.info('Response of operation: '+operation)
    app.logger.info(json.dumps(response))

@app.route('/')
def base():
    return Response(response=json.dumps({"Status": "UP"}),
                    status=200,
                    mimetype='application/json')

@app.route('/mongodb', methods=['GET'])
def mongo_read():
    data = request.json
    if data is None or data == {}:
        app.logger.info('Missing DB Conenction Informaion');
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data)
    response = obj1.read()
    logResponse(response, 'Read');
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')

@app.route('/mongodb/<string:name>', methods=['GET'])
def mongo_read_one(name):
    data = request.json
    if data is None or data == {}:
        app.logger.info('Missing DB Conenction Informaion');
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')

    filter = {
        'First_Name' : name
    }

    obj1 = MongoAPI(data)
    response = obj1.getDetails(filter);
    logResponse(response, 'Details');
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')


@app.route('/mongodb', methods=['POST'])
def mongo_write():
    data = request.json
    if data is None or data == {} or 'Document' not in data:
        app.logger.error('Missing DB Conenction Informaion');
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data)
    response = obj1.write(data)
    logResponse(response, 'Insert');
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')

@app.route('/mongodb', methods=['PUT'])
def mongo_update():
    data = request.json
    if data is None or data == {} or 'Filter' not in data:
        app.logger.error('Missing DB Conenction Informaion');
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data)
    response = obj1.update(data)
    logResponse(response, 'Update');
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')


@app.route('/mongodb', methods=['DELETE'])
def mongo_delete():
    data = request.json
    if data is None or data == {} or 'Filter' not in data:
        app.logger.error('Missing DB Conenction Informaion');
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data)
    response = obj1.delete(data)
    logResponse(response, 'Delete');
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')
  
if __name__ == '__main__':
    ##Add logger
    handler = RotatingFileHandler('flask_rest.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    

    app.run(debug=True, port=5001, host='0.0.0.0')