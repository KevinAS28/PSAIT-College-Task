import json
import traceback
import requests

from django.http import JsonResponse
from django.shortcuts import render
from django.core.handlers.wsgi import WSGIRequest
from django.conf import settings

# Create your views here.

ENV_VARS = settings.ENV_VARS


def send_orang(request: WSGIRequest):
    try:
        if request.method == 'POST':
            data = request.POST
            host = data['host']
            json_send = {
                'nama': data['nama'],
                'umur': data['umur']
            }
            response = requests.post(host, data=json.dumps(json_send))
            return JsonResponse(json.loads(response.text))
        elif request.method == 'GET':
            return render(request, 'test.html')
    except Exception as error:
        error_brief = error
    error_data = {
        'error_brief': str(error_brief),
        'error_long': str(traceback.format_exc()),
        'status': 1,
        'status_str': 'Error'
    }

    return JsonResponse(error_data)


def orang_page(request: WSGIRequest):
    host = '127.0.0.1'
    text = requests.post(f'http://{host}:8080/authentication/get_token',
                         data='{"username": "admin", "password": "123"}').text
    print(text)
    token = json.loads(text)['token']
    params = {'token': token}
    orangs = (requests.get(
        f'http://{host}:8080/api/get_orang', params=params).text)
    print(orangs)
    orangs = json.loads(orangs)['data']
    print(type(orangs))
    return render(request, 'orang.html', {'orangs': orangs['orang']})


def sentiment_analysis(request: WSGIRequest):
    if request.method == 'GET':
        return render(request, 'sentiment_analysis.html')
    elif request.method == 'POST':
        key = ENV_VARS['GCP_API_KEY']
        data = {
            "document": {
                "type": "PLAIN_TEXT",
                "content": request.POST['context']
            },
            "encodingType": "UTF8"
        }
        resp = requests.post(
            f'https://language.googleapis.com/v1/documents:analyzeEntities?key={key}', data=json.dumps(data))
        print(resp.text)
        entities = json.loads(resp.text)['entities']
        all_entities = [{e['type']:e['name']} for e in entities]
        return render(request, 'sentiment_analysis.html', {'all_entities':all_entities})
