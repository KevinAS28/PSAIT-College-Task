from django.db import models

# Create your models here.
class Mahasiswa(models.Model):
    nim = models.CharField(max_length=10, primary_key=True)
    nama = models.CharField(max_length=20)
    alamat = models.CharField(max_length=40)
    tanggal_lahir = models.DateField(null=True, blank=True)

class MataKuliah(models.Model):
    kode_mk = models.CharField(max_length=10, primary_key=True) 
    nama_mk = models.CharField(max_length=30)
    sks = models.IntegerField(2)

class Perkuliahan(models.Model):
    id_perkuliahan = models.AutoField(primary_key=True)
    nim = models.ForeignKey(Mahasiswa, to_field='nim', on_delete=models.CASCADE) # foreign key ke nim pada mahasiswa
    kode_mk = models.ForeignKey(MataKuliah, to_field='kode_mk', on_delete=models.CASCADE) # foreign key ke kode_mk pada mata kuliah
    nilai = models.FloatField() #Di python tidak ada double, hanya ada integer dan float

