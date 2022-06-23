app_name = 'web'

from django.urls import path
from .views import *


urlpatterns = [
    path('send_orang', send_orang),
    path('orang_page', orang_page),
    path('external_api', external_api),
    path('table', table),
    path('form', form),
    path('form_multi_db', form_multi_db),
    path('tg_gcp_permission', tg_gcp_compute)
]