app_name = 'api'

from django.urls import path
from .views import *


urlpatterns = [
    path('get_orang', get_orang),
    path('update_orang', update_orang),
    path('create_orang', create_orang),
    path('delete_orang', delete_orang),
]