from datetime import datetime
import json
from django.http import JsonResponse
import authentication.models as models
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist
import authentication.auth_util as auth_util


def login(*args, **kwargs):
    def decorator(fun):
        def wrapper(*args, **kwargs):
            request = args[0]
            if request.method == 'GET':
                username = request.GET['username']
                password = request.GET['password']
            elif request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                data = json.loads(request.body)
                username = data['username']
                password = data['password']   
            else:
                response = {'success': False, 'message': 'Invalid method'}
                print('Response:', response)
                return JsonResponse(response)

            user = models.UserAuthentication.objects.filter(username=username, password=password)
            if user.exists():
                print(f"Login success: {user[0].username} -> {request.build_absolute_uri()}")
                result = fun(*args, **kwargs)
                auth_success = {'success': True, 'message': 'OK', 'user': model_to_dict(user[0])}
                response = {**({f'data{i}': json.loads(key) for i, key in enumerate(result)}), **auth_success}
                print('Response:', response)
                response = JsonResponse(response)
                # print('readable', response.)
                return response

            else:
                print(f"Invalid authentication {username}|{password}")
                response = {'success': False, 'message': 'Invalid Authentication'}
                print('Response:', response)
                return JsonResponse(response)
        return wrapper
    return decorator



def token_get(username, password):
    try:
        user = models.UserAuthentication.objects.get(username=username, password=password)
        # role = models.UserRole.objects.get(id=user.role)
        print(user.role)
        token = (auth_util.token_hash((username+password+str(datetime.now())).encode('utf-8')))
        user.token = token
        user.token_expired = models.expire()
        user.save()
        return token
    except ObjectDoesNotExist:
        return False

def token_refresh(token):
    try:
        user = models.UserAuthentication.objects.get(token=token)
        username = user.username
        password = user.password
        token = (auth_util.token_hash((username+password+str(datetime.now())).encode('utf-8'))).hexdigest()
        user.token = token
        user.token_expired = models.expire()
        user.save()        
        return token
    except ObjectDoesNotExist:
        return False

def token_delete(token):
        try:
            user = models.UserAuthentication.objects.get(token=token)
            username = user.username
            password = user.password
            token = (auth_util.token_hash((username+password+str(datetime.now())).encode('utf-8'))).hexdigest()
            user.token = token
            user.token_expired = datetime.now()
            user.save()        
            return user
        except ObjectDoesNotExist:
            return False

def token_auth_core(token, roles):
    try:
        if len(roles)==0:
            return None
        elif (len(roles)>0) and (roles[0]=='*'):
            user = models.UserAuthentication.objects.get(token=token)
        else:
            role_objects = list(models.UserRole.objects.filter(role_name__in=roles))
            user = models.UserAuthentication.objects.get(token=token, roles__in=role_objects)
        if user.token_expired>=datetime.now(user.token_expired.tzinfo):
            return user
        else:
            return None
    except ObjectDoesNotExist:
        return None

def token_auth(roles=['*']):
    def decorator(fun):
        def wrapper(*args, **kwargs):
            request = args[0]

            try:
                if request.method == 'GET':
                    token = request.GET['token']
                elif request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                    data = json.loads(request.body)
                    token = data['token']
                else:
                    token = None
            except:
                print(f"no token")
                response = {'success': False, 'message': 'Invalid Authentication'}
                print('Response:', response)
                return JsonResponse(response)

            if token is None:
                response = {'success': False, 'message': 'Invalid method'}
                print('Response:', response)
                return JsonResponse(response)

            user = token_auth_core(token, roles)
            if user:
                print(f"Login success: {user} -> {request.build_absolute_uri()}")
                result = fun(*args, **kwargs)
                auth_success = {'success': True, 'message': 'OK'}
                response = {'data': result, 'auth': auth_success}
                print('Response:', response)
                response = JsonResponse(response)
                # print('readable', response.)
                return response

            else:
                print(f"Invalid token")
                response = {'success': False, 'message': 'Invalid Authentication'}
                print('Response:', response)
                return JsonResponse(response)
        return wrapper
    return decorator
