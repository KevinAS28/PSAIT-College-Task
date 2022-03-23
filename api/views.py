import json
import traceback

from django.forms import model_to_dict
from django.core.handlers.wsgi import WSGIRequest
from django.views.decorators.http import require_http_methods

from authentication.auth_core import token_auth
import case3.models as models

# Create your views here.

@token_auth(roles=['*'])
@require_http_methods(['GET'])
def get_orang(request:WSGIRequest):
    return {'orang': [model_to_dict(i) for i in models.Orang.objects.all()]}

@require_http_methods(['PUT'])
@token_auth(roles=['*'])
def update_orang(request:WSGIRequest):
    try:
        data = json.loads(request.body)
        idorang, nama, umur = data['id'], data['nama'], data['umur']
        orang = models.Orang.objects.get(id=idorang)
        orang.nama = nama
        orang.umur = umur
        orang.save()
        response = {
            'saved_models': model_to_dict(orang),
            'status':0,
            'status_str':'success'
        }
        return (response)
    except Exception as error:
        error_data = {
            'error_brief': str(error),
            'error_long': str(traceback.format_exc()),
            'status': 1,
            'status_str': 'Error'
        }
        return (error_data)

@require_http_methods(['DELETE'])
@token_auth(roles=['*'])
def delete_orang(request:WSGIRequest):
    
    try:
        data = json.loads(request.body)
        orang = models.Orang.objects.get(nama=data['nama'], umur=data['umur'])
        orang.delete()
        response = {
            'deleted_models': model_to_dict(orang),
            'status':0,
            'status_str':'success'
        }
        return (response)
    except Exception as error:
        error_data = {
            'error_brief': str(error),
            'error_long': str(traceback.format_exc()),
            'status': 1,
            'status_str': 'Error'
        }

        return (error_data)

@require_http_methods(['POST'])
@token_auth(roles=['*'])
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
        return response
    except Exception as error:
        error_data = {
            'error_brief': str(error),
            'error_long': str(traceback.format_exc()),
            'status': 1,
            'status_str': 'Error'
        }

        return response
