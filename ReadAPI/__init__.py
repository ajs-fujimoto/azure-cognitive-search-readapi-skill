import logging
import azure.functions as func
import json
import io
import os
import base64
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from . import readapi

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Read API v3.2 Custom Skill: Python HTTP trigger function processed a request.')

    try:
        # get request body
        body = req.get_json()
        # prep return shape
        records = { 'values': [] }
        recordId = ""

        # get key and endpoint from Environment variable
        computerVisionKey = os.environ['COMPUTER_VISION_KEY']
        computerVisionEndpoint = os.environ['COMPUTER_VISION_ENDPOINT']

        # set credentials
        credentials = CognitiveServicesCredentials(computerVisionKey)
        # create client
        client = ComputerVisionClient(computerVisionEndpoint, credentials)

        for record in body["values"]:
            recordId = record["recordId"]
                
            # Get the base64 encoded image
            encoded_image = record["data"]["image"]["data"]
            base64Bytes = encoded_image.encode('utf-8')
            image = base64.b64decode(base64Bytes)

            # calls the read api of the specified image. 
            result = readapi.read_text(client, io.BytesIO(image))
            temp_line_text = []
            if result.status == OperationStatusCodes.succeeded:
                for text_result in result.analyze_result.read_results:
                    for line in text_result.lines:
                        temp_line_text.append(line.text)

                merged_text = "".join(temp_line_text)
                records['values'].append(makeRes(recordId, readapi.remove_spaces(merged_text)))

            # Error from Cognitive Services
            else:
                code = result['error']['code']
                message = result['error']['message']
                logging.error(f'CogSvc Error {code}: {message}')
                records['values'].append(makeErrRes(recordId, code, message, 'Cognitive Services Error'))

    except Exception as error:
        logging.exception('Python Error')
        records['values'].append(makeErrRes(recordId, '500', f'{type(error).__name__}: {str(error)}', 'Python Error'))

    return func.HttpResponse(body=json.dumps(records), headers={ 'Content-Type': 'application/json', "Access-Control-Allow-Origin": "*" })


def makeRes(recordId, text):
    response = {
        'recordId': recordId,
        'data': {
            'ocrtext': text,
            'error': {}
        }
    }
    return response

def makeErrRes(recordId, code, message, type):
    response = {
        'recordId': recordId,
        'data': {
            'ocrtext': "",
            'error': {
                'code': code,
                'message': message,
                'type': type
            }
        }
    }
    return response