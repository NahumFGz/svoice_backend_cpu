import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Bienvenido a esta wea xD"


@app.route("/separate", methods=['POST'])
def predict():
    json = request.get_json(force=True)
    s3id = json['s3id']
    print('------------> ' + s3id)

    os.system('python ./separate.py')
    
    return 'S1 & S2 generados'