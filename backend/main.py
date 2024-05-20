from flask import Flask, jsonify, send_from_directory
from pymongo import MongoClient
import os
from bson import ObjectId

from dotenv import load_dotenv 

load_dotenv()

app = Flask(__name__, static_folder='../frontend/build', static_url_path='')

from flask_cors import CORS
CORS(app)

URI = os.getenv('URI')

client = MongoClient(URI)
db = client['newsagg']
articles = db['articles']

# class JSONEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, ObjectId):
#             return str(obj)
#         return json.JSONEncoder.default(self, obj)

# app.json_encoder = JSONEncoder

@app.route('/records', methods=['GET'])
def get_all_records():
    try:
        results = articles.find({}).sort("date", -1).limit(50)
        results = list(results)
        
        for result in results:
            result['_id'] = str(result['_id'])
        print(len(results))
        return jsonify(results), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=3000)