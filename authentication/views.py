import json
from django.http import JsonResponse
import authentication.models as models

import authentication.auth_core as auth_core

def get_token(request):
    print(request.body)
    data = json.loads(request.body)
    username = data['username']
    password = data['password']
    token = auth_core.token_get(username, password)
    if token:
        response_data = {
            'status': 0,
            'token': token
        }
    else:
        response_data = {
            'error_brief': '',
            'error_long': '',
            'status': 1,
            'status_str': 'Failed Get Token'
        }

    return JsonResponse(response_data)

def refresh_token(request):
    data = json.loads(request.body)
    old_token = data['token']
    new_token = auth_core.token_refresh(old_token)
    if new_token:
        return JsonResponse({'token': new_token})
    return JsonResponse({'token': ''})

def delete_token(request):
    data = json.loads(request.body)
    token = data['token']
    result = auth_core.token_delete(token)
    if result:
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def register_user(request):
    try:
        data = json.loads(request.body)
        username = data['username']
        password = data['password']
        role = data['role']
        userauth = models.UserAuthentication(
            username=username,
            password=password,
            role=role
        )
        userauth.save()
        return JsonResponse({'success': True})
    except:
        return JsonResponse({'success': False})

