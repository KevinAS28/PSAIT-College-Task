from django.core.handlers.wsgi import WSGIRequest

from authentication.auth_core import *

import case3.models as models



@token_auth(roles=['*'])
def test(request:WSGIRequest):
    return {'Hello': 'World'}

    

