app_name = 'web'

from django.urls import path
from .views import *


urlpatterns = [
    path('send_orang', send_orang),
    path('orang_page', orang_page),
    path('sentiment_analysis', sentiment_analysis)
]