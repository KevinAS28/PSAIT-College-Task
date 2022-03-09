from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from django.core.handlers.wsgi import WSGIRequest
import json
import traceback
import case3.models as models
import requests

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

    


def create_orang(request:WSGIRequest):
    
    try:
        data = json.loads(request.body)
        orang = models.Orang(nama=data['nama'], umur=data['umur'])
        orang.save()
        response = {
            'saved_models': model_to_dict(orang),
            'status':0,
            'status_str':'success'
        }
        return JsonResponse(response)
    except Exception as error:
        error_data = {
            'error_brief': str(error),
            'error_long': str(traceback.format_exc()),
            'status': 1,
            'status_str': 'Error'
        }

        return JsonResponse(error_data)

    

    