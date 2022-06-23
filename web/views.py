import json
import traceback
import requests

from case3 import models as case3_models

from django.http import JsonResponse
from django.shortcuts import render
from django.core.handlers.wsgi import WSGIRequest
from django.conf import settings
from django.views.decorators.http import require_http_methods
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


def entity_extraction(request: WSGIRequest):
    if request.method == 'GET':
        return render(request, 'entity_extraction.html')
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
        return render(request, 'entity_extraction.html', {'all_entities': all_entities})


def table(request):
    return render(request, 'table.html')


def form(request):
    return render(request, 'form.html')


@require_http_methods(['GET', 'POST'])
def form_multi_db(request: WSGIRequest):
    saved = False
    response = None
    response_status = None

    if request.method == 'POST':
        try:
            response = requests.post(settings.BACKUP_DB_API, data=json.dumps({
                "action": "CREATE",
                "tables": [
                    {
                        "app_label": "case3",
                        "model_name": "Orang",
                        "to_creates": [
                            {key:value[0] for key, value in dict(request.POST).items()}
                        ]
                    }
                ]
            }))
            orang = case3_models.Orang(
                nama=request.POST['nama'], umur=request.POST['umur'])
            orang.save()
            response_status = True
        except:
            response = traceback.format_exc()
            print('Error', response)
            response_status = False

        saved = True

    return render(request, 'form_multi_db.html', {'saved': saved, 'response': response, 'response_status': response_status})

def tg_gcp_compute(request: WSGIRequest):
    message = 'No Message'
    URL = 'http://172.29.82.245:9999/api/tg_gcp_permission'
    username_access = dict()
    if request.method=='POST':
        if request.POST['type_post']=='new':
            post = dict(request.POST)
            username_access[post['new_username'][0]] = bool(post['new_access'][0])
        else:
            username_to_switches = [i.lstrip('switch_') for i in dict(request.POST) if i.startswith('switch_')]
            message = str(username_to_switches)
            
            response = requests.put(URL, data=json.dumps({'username_access': username_access})).text
            response = json.loads(response)
            username_access = response['username_access']
            
            new_username_access = {ua['username']: not ua['access'] for ua in username_access if ua['username'] in username_to_switches}
            response = requests.put(URL, data=json.dumps({'username_access': new_username_access})).text
            response = json.loads(response)
            username_access = dict()


    response = requests.put(URL, data=json.dumps({'username_access': username_access})).text
    response = json.loads(response)
    username_access = response['username_access']
    

    body = {'msg': message, 'username_access': username_access}

    return render(request, 'tg_gcp_permision.html', body)