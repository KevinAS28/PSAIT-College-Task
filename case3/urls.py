app_name = 'case3'

from django.urls import path
from .views import *


urlpatterns = [
    path('test', test),

]