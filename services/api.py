import io
import os
import glob

from flask import Flask, jsonify, request, json
from flask_cors import CORS


import boto3

from google.cloud import speech

from svoice.separate_api import separate as svoice_separate


app = Flask(__name__)
CORS(app)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/ubuntu/speechtotext-321901-1976c2a44069.json"

@app.route("/")
def home():
    return "<h1>API Prototype</h1><p>Api for separate confluent audios</p>"


@app.route("/separate"
    , methods=['POST']
)
def predict():
    try:

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

        return  jsonify({
                "message": "success",
                "audios": json.dumps([f.replace('\\', '/') for f in out_files])
            })
    except Exception as e:
        return jsonify({
                "message": "fail",
                "message_error": str(e)
            })

@app.route("/translate"
    , methods=['POST']
)
def translate():

    try:

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

        wav_file = 'demo/mix/{}'.format(folder[-1])
        flac_file = wav_file.replace('.wav', '.flac')



        # Convert WAV to FLAC
        cmd = 'ffmpeg -i "{}" "{}"'.format(wav_file, flac_file)
        os.system(cmd)

        # Translate
        client = speech.SpeechClient()

        # Full path of the audio file, Replace with your file name
        file_name = flac_file


        with open(file_name,'rb') as f:
            content = f.read()
            audio = speech.RecognitionAudio(content=content)

        config = speech.RecognitionConfig(
            enable_automatic_punctuation=True,
            encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
            audio_channel_count=1,
            language_code="es-PE",
            model="default"
        )


        # Sends the request to google to transcribe the audio
        responses = client.recognize(request={
            "config": config,
            "audio": audio
        })

        text_translate = ""


        # Reads the response
        for result in responses.results:
            text_translate += result.alternatives[0].transcript


        mix_files = glob.glob('demo/mix/*')
        for f in mix_files:
            try:
                os.remove(f)
            except:
                pass

        
        file_txt_name = flac_file.split('.')[0] + '.txt'
        file_txt = open(file_txt_name, "w+") 
        file_txt.write(text_translate) 
        file_txt.close() 

        s3_client.upload_file(
            file_txt_name,
            bucket,
            'out/{}'.format(
                file_txt_name.replace('\\', '/').split('/')[-1]
            )
        )
            
        print(6)
        return  jsonify({
                "message": "success",
                "translate": text_translate,
                "translate_file": 'out/{}'.format(file_txt_name.replace('\\', '/').split('/')[-1])
            })
    except Exception as e:
        return jsonify({
                "message": "fail",
                "message_error": str(e)
            })

if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get('PORT', 5000)))
