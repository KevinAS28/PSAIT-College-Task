import requests
from django.shortcuts import render
import time, json
from django.conf import settings
from threading import Thread
from google.cloud import compute_v1 as gcpvm
from sympy import per
from api import models as api_models
import api

ENV_VARS = settings.ENV_VARS
TG_TOKEN = ENV_VARS['TG_API_KEY']
authorized_usernames = [
    'KevinAS28',
    'KevinAS288',
]
last_chat = None
gcpvm_client = gcpvm.InstancesClient.from_service_account_json('com.json')

def to_json_key(obj):
    converters = [dict, lambda x: x.__dict__, int, float, str, bool]
    for conv in converters:
        try:
            return conv(obj)
        except:
            pass
    return None


def dict_filter_keys(obj, keys=None, safe_json=False):
    conv_key = lambda key: to_json_key(key) if safe_json else key
    if type(obj)==dict:
        check = lambda key, obj: True if keys is None else (key in obj)
        new_dict = {conv_key(key): obj[key] for key in keys if check(key, obj)}
        return new_dict
    else:
        check = lambda key, obj: True if keys is None else (hasattr(obj, key))
        new_dict = {conv_key(key): getattr(obj, key) for key in keys if check(key, obj)}
        return new_dict

def keep_try(max_try=-1, fun=lambda: 'replace this function', *args, **kwargs):
    try_count = 0
    last_error = None
    while try_count!=max_try:
        try:
            return fun(*args, **kwargs)
        except Exception as e:
            last_error = e
            try_count += 1
    return last_error


def parse_update(data):
    chats = []
    for d0 in data['result']:
        if ('message' in d0):                
            d1 = {
                'chat_id': d0['message']['chat']['id'],
                'from_username': d0['message']['from']['username'],
                'chat_text': d0['message']['text'],
                'date': d0['message']['date'],
                'from_type': 'private'
            }
            if not (d1['from_username'] in authorized_usernames):
                continue
            chats.append(d1)
    return chats

def send_message(chat_id, text):
    URL = f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': text
    }
    return json.loads(requests.get(url=URL, data=data, timeout=5).text)

def log(text):
    text = str(text)
    with open('log.txt', 'a+') as logger:
        logger.write(f'{text}\n')
    print(text)

def list_instances(chat_dict=None, name=None):
    request_args = dict(
        project='quickstart-1577356419888',
        zone='us-central1-a',
        # instance='6274371430708212565'
    )
    results = [dict_filter_keys(i, 'id kind name network_interfaces status'.split(' '), safe_json=True) for i in keep_try(-1, gcpvm_client.list, **request_args)]
    if name is None:
        if not (chat_dict is None):
            def serializer(obj):
                try:
                    return obj.__dict__
                except:
                    return str(obj)
            def to_json(obj):
                try:
                    return json.dumps(i, indent=4, default=serializer)
                except:
                    return str(i)
            keep_try(-1, send_message, chat_dict['chat_id'], '\n\n\n'.join([str(i) for i in list(results)]))
        else:
            return list(results)
    else:
        the_instance = None
        for i in results:
            if i['name']==name:
                the_instance = i
                break
        
        if not (chat_dict is None):
            keep_try(-1, send_message, chat_dict['chat_id'], str(list(results)))
        else:
            return the_instance, list(results)
    
    
def start_instance(chat_dict: dict, instance_name: str):
    the_instance, all_instances = list_instances(name=instance_name)
    if the_instance is None:
        formatted_allinstances = "\n".join(all_instances)
        keep_try(-1, send_message, chat_dict['chat_id'], f'Instance name "{instance_name}". Here are valid instances: {formatted_allinstances}')
        return
    else:
        keep_try(-1, send_message, chat_dict['chat_id'], 'Please wait while the VM is starting, I will get to you back ASAP')
    request_args = dict(
        project='quickstart-1577356419888',
        zone='us-central1-a',
        instance=str(the_instance['id'])
    )
    result = gcpvm_client.start(**request_args)
    keep_try(-1, send_message, chat_dict['chat_id'], f'The instance {instance_name} has been started with status: {result}')

    

def stop_instance(chat_dict, instance_name):
    the_instance, all_instances = list_instances(name=instance_name)
    if the_instance is None:
        formatted_allinstances = "\n".join(all_instances)
        keep_try(-1, send_message, chat_dict['chat_id'], f'Instance name "{instance_name}". Here are valid instances: {formatted_allinstances}')
        return
    else:
        keep_try(-1, send_message, chat_dict['chat_id'], 'Please wait while the VM is stopping, I will get to you back ASAP')
    request_args = dict(
        project='quickstart-1577356419888',
        zone='us-central1-a',
        instance=str(the_instance['id'])
    )
    result = gcpvm_client.stop(**request_args)
    keep_try(-1, send_message, chat_dict['chat_id'], f'The instance {instance_name} has been stopped with status: {result}')


COMMAND_FUNCTION_MAP = {
    'start_instance': start_instance,
    'stop_instance': stop_instance,
    'list_instances': list_instances
}


def process_new_chat(chat_dict: dict):
    chat_text: str = chat_dict['chat_text']
    if chat_text.startswith('> '):
        permitted_usernames = api_models.TgGcpAccess.objects.filter(tg_username=chat_dict['from_username'])
        if len(permitted_usernames)==0:
            keep_try(-1, send_message, chat_dict['chat_id'], 'You are not permitted')
            return 
        if not permitted_usernames[0].access:
            keep_try(-1, send_message, chat_dict['chat_id'], 'You are not permitted')
            return 

        log('command received')
        # send_message(chat_dict['chat_id'], 'This is a valid command')
        text = chat_text[2:]
        command, *args = text.split(' ')
        print('command:', command)
        if command in COMMAND_FUNCTION_MAP:
            log('valid command')
            COMMAND_FUNCTION_MAP[command](*([chat_dict]+args))
            return
    log('not a command')
    keep_try(-1, send_message, chat_dict['chat_id'], 'This is an invalid command')
    

# Create your views here.
def tg_bot_monitor(refresh_seconds=3):
    global last_chat
    URL = f'https://api.telegram.org/bot{TG_TOKEN}/getUpdates'
    while True:
        log('checking update...')
        data = json.loads(keep_try(-1, requests.get, url=URL, timeout=5).text)
        update = parse_update(data)
        new_chat = update[-1]
        print(new_chat)
        if new_chat==last_chat:
            print('nothing new')
            continue
        print('new')
        log(update)
        last_chat = new_chat
        process_new_chat(last_chat)
        time.sleep(refresh_seconds)

Thread(target=tg_bot_monitor).start()