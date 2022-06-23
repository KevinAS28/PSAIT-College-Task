import requests, json

token = '1000342832:AAEsBxW2JEtwxKGKRfxDMHiNTuaEk0yqKNc'

url = f'https://api.telegram.org/bot{token}/getUpdates'

params = {
    'chat_id': '580431041',
    'text': 'Hello there'
}

authorized_usernames = [
    'KevinAS28',
    'KevinAS288',
]

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
            chats.append(d1)
    return chats

# print(parse_update(json.loads(requests.get(url=url, data=params).text)))

from google.cloud import compute_v1 as com

client = com.InstancesClient.from_service_account_json('com.json')
instance = dict(
    project='quickstart-1577356419888',
    zone='us-central1-a',
    # instance='6274371430708212565'
)
# result = client.start(**instance)
# result = client.stop(**instance)
result = client.list(**instance)

# print(result)
# print('\n'*4)
# print(list(result)[0].name)

def to_dict(obj):
    if not (type(obj)==dict):
        try:
            obj = obj.__dict__
        except:
            def fun(): pass
            obj = {key:getattr(obj, key) for key in dir(obj) if not (type(getattr(obj, key))==type(fun))}
    return obj

def dict_filter_keys(the_dict, keys):
    the_dict = to_dict(the_dict)
    to_delete_keys = []
    for key in the_dict:
        if not (key in keys):
            to_delete_keys.append(key)
    for key in to_delete_keys:
        del the_dict[key]
    return the_dict


print(dict_filter_keys(result, ['id', 'name']))
