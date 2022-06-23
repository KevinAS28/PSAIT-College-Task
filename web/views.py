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
    print('orang_page')
    host = '172.29.80.1:8082'
    text = requests.post(f'http://{host}/token_authentication/get_token',
                         data='{"username": "admin", "password": "admin"}').text
    print(text)
    token = json.loads(text)['token']
    params = {'token': token}
    headers = {'token': token}
    orangs = (requests.get(
        f'http://{host}/api/get_orang', params=params, headers=headers).text)
    print(orangs)
    orangs = json.loads(orangs)
    print(type(orangs))
    return render(request, 'orang.html', {'orangs': orangs['orang']})


def external_api(request: WSGIRequest):
    if request.method == 'GET':
        return render(request, 'entity_extraction.html')
    elif request.method == 'POST':
        key = ENV_VARS['GCP_API_KEY']
        # data = {
        #     "document": {
        #         "type": "PLAIN_TEXT",
        #         "content": request.POST['context']
        #     },
        #     "encodingType": "UTF8"
        # }

        # SEARCH_PLACE_API = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
        # search_place_parameters = {
        #     'key': key,
        #     'query': request.POST['context']
        # }
        # request_response = requests.get(SEARCH_PLACE_API, params=search_place_parameters)    

        url = f'https://api.telegram.org/bot{ENV_VARS["TG_API_KEY"]}/sendMessage'
        data = {
            'chat_id': '580431041',
            'text': request.POST['context']
        }


        request_response = requests.get(url=url, data=data)
        # resp = requests.post(
            # f'https://language.googleapis.com/v1/documents:analyzeEntities?key={key}', data=json.dumps(data))
        print(request_response.text)
        entities = json.loads(request_response.text)['result']
        all_entities = [entities['chat'], entities['from']]#[{e['name']:e['formatted_address']} for e in entities]
        print(all_entities)
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