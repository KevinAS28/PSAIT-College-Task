import json
import traceback
import requests

from django.http import JsonResponse
from django.shortcuts import render
from django.core.handlers.wsgi import WSGIRequest

# Create your views here.

def send_orang(request:WSGIRequest):
    try:
        if request.method=='POST':
            data = request.POST
            host = data['host']
            json_send = {
                'nama': data['nama'],
                'umur': data['umur']
            }
            response = requests.post(host, data=json.dumps(json_send))
            return JsonResponse(json.loads(response.text))
        elif request.method=='GET':
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

def orang_page(request:WSGIRequest):
    host = '127.0.0.1'
    text = requests.post(f'http://{host}:8080/authentication/get_token', data='{"username": "admin", "password": "123"}').text
    # print(text)
    token = json.loads(text)['token']
    orangs = json.loads(requests.post(f'http://{host}:8080/case3/getorang', data='{"token": "%s"}'%(token)).text)['data']
    print(type(orangs))
    return render(request, 'orang.html', {'orangs': orangs['orang']})
