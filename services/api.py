from flask import Flask, jsonify, request
from flask_cors import CORS
from svoice.separate_api import separate as svoice_separate
import boto3

import os
import glob

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "<h1>API Prototype</h1><p>Api for separate confluent audios</p>"


@app.route("/separate"
    , methods=['POST']
)
def predict():
    s3id = request.values.get('s3id')
    aws_access_key_id = request.values.get('aws_access_key_id')
    aws_secret_access_key = request.values.get('aws_secret_access_key').replace(' ', '+')

    session = boto3.Session(
        aws_access_key_id = aws_access_key_id,
        aws_secret_access_key = aws_secret_access_key
    )

    s3_client = session.client("s3")

    # Download the file from S3
    _, _, bucket, *folder = s3id.split('/')
    
    s3_client.download_file(bucket, '/'.join(folder), 'demo/mix/{}'.format(folder[-1]))

    svoice_separate(
        out_dir = "./demo/out",
        mix_dir = "./demo/mix",
        model_path = "./demo/checkpoint.th",        
        local_out_dir = './demo/out'
    )
    
    mix_files = glob.glob('demo/mix/*')
    for f in mix_files:
        os.remove(f)    
    
    out_files = glob.glob('demo/out/*')
    for f in out_files:
        s3_client.upload_file(
            f,
            bucket,
            'out/{}'.format(
                f.replace('\\', '/').split('/')[-1]
            )
        )
        os.remove(f)

    return 'Audio separated'