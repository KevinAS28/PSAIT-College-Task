import json
import traceback

from django.forms import model_to_dict
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.apps import apps

from sympy import per

from token_authentication.auth_core import token_auth
from api.models import *

# Create your views here.

@token_auth(roles=['*'])
@require_http_methods(['GET'])
def get_orang(request:WSGIRequest):
    return {'orang': [model_to_dict(i) for i in Orang.objects.all()]}

@require_http_methods(['PUT'])
@token_auth(roles=['*'])
def update_orang(request:WSGIRequest):
    try:
        data = json.loads(request.body)
        idorang, nama, umur = data['id'], data['nama'], data['umur']
        orang = Orang.objects.get(id=idorang)
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
        orang = Orang.objects.get(nama=data['nama'], umur=data['umur'])
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
        orang = Orang(nama=data['nama'], umur=data['umur'])
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


def nilai_raw_query(request):
    with connection.cursor() as cursor:
        cursor.execute('''SELECT api_perkuliahan.nim_id, api_mahasiswa.nama, api_mahasiswa.alamat,  api_mahasiswa.tanggal_lahir, api_matakuliah.kode_mk, api_matakuliah.nama_mk, api_matakuliah.sks, api_perkuliahan.nilai FROM api_perkuliahan JOIN api_mahasiswa  ON api_mahasiswa.nim=api_perkuliahan.nim_id JOIN api_matakuliah  ON api_matakuliah.kode_mk=api_perkuliahan.kode_mk_id;''')
        columns = [col[0] for col in cursor.description]
        return JsonResponse({'nilai': [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]})

def my_custom_sql(self):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE bar SET foo = 1 WHERE baz = %s", [self.baz])
        cursor.execute("SELECT foo FROM bar WHERE baz = %s", [self.baz])
        row = cursor.fetchone()

    return row

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

@require_http_methods(['POST'])
def backup_db(request: WSGIRequest):
    data = json.loads(request.body)
    print('data', data)
    if data['action']=='CREATE':
        for table in data['tables']:
            table_model = apps.get_model(app_label=table['app_label'], model_name=table['model_name'])
            for to_create in table['to_creates']:
                table_model(**to_create).save() 
    return JsonResponse({'OK': 'OK'})

@require_http_methods(['PUT'])
# @token_auth(roles=['*'])
def tg_gcp_permission(request: WSGIRequest):
    data = json.loads(request.body)
    username_access = data['username_access']
    print(username_access)
    users = TgGcpAccess.objects.filter(tg_username__in=list(username_access.keys()))
    for u in users:
        u.access = username_access[u.tg_username]
        u.save()
        del username_access[u.tg_username]
    for user, access in username_access.items():
        TgGcpAccess(tg_username=user, access=access).save()
    return JsonResponse({'success': True, 'username_access': [{'username': i.tg_username, 'access': i.access} for i in TgGcpAccess.objects.all()]})

