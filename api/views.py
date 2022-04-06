import json
import traceback

from django.forms import model_to_dict
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from sympy import per

from authentication.auth_core import token_auth
from api.models import *

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

def test_perkuliahan(request:WSGIRequest):
    perkuliahan = Perkuliahan.objects.all().select_related('nim', 'kode_mk')
    
    return JsonResponse({
        'query': str(perkuliahan.query),
        'perkuliahan': [model_to_dict(o) for o in list(perkuliahan)]
    })



@require_http_methods(['GET'])
def show_nilai_mahasiswa(request:WSGIRequest):
    try:
        data = json.loads(request.body)
        nim = data['nim']
    except:
        return JsonResponse({'nilai': [model_to_dict(o) for o in list(Perkuliahan.objects.all())]})
    get_nilai_mk = lambda o: {'mk': MataKuliah.objects.get(kode_mk=o['kode_mk']).nama_mk, 'nilai': o['nilai']}
    return JsonResponse({'nilai': [get_nilai_mk(model_to_dict(o)) for o in Perkuliahan.objects.filter(nim__nim=nim)]})

@require_http_methods(['POST', 'PATCH', 'DELETE'])
def nilai(request:WSGIRequest):
    data = json.loads(request.body)

    nilai = data['nilai']
    kode_mk_id = data['kode_mk_id']
    nim_id = data['nim_id']

    try:
        mk = MataKuliah.objects.get(kode_mk=kode_mk_id)
        mahasiswa = Mahasiswa.objects.get(nim=nim_id)
    except:
        return JsonResponse({'error': 'MK atau Mahasiswa tidak ditemukan'})

    if request.method=='POST':
        perkuliahan = Perkuliahan.objects.filter(nim=mahasiswa, kode_mk=mk)

        if (len(perkuliahan)!=0):
            return JsonResponse({'error': f'Mahasiswa sudah punya nilai untuk MK ini: {perkuliahan[0].nilai}'})        

        perkuliahan = Perkuliahan(
            nilai=nilai,
            nim=mahasiswa,
            kode_mk=mk
        )

        perkuliahan.save()

        return JsonResponse({'saved': model_to_dict(perkuliahan)})

    if request.method=='PATCH':
        perkuliahan = Perkuliahan.objects.get(kode_mk=mk, nim=mahasiswa)
        perkuliahan.nilai = nilai
        perkuliahan.save()
        
        return JsonResponse({'updated': model_to_dict(perkuliahan)})

    if request.method=='DELETE':
        perkuliahan = Perkuliahan.objects.get(kode_mk=mk, nim=mahasiswa)
        perkuliahan.delete()
        return JsonResponse({'deleted': model_to_dict(perkuliahan)})
