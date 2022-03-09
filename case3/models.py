from django.db import models

# Create your models here.
class Orang(models.Model):
    nama = models.CharField(max_length=50)
    umur = models.IntegerField()