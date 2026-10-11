from django.db import models

class Reg_Log_information(models.Model):
    name = models.CharField(max_length=35)
    UserName = models.CharField(max_length=35)
    mobile = models.CharField()
    reg_num = models.CharField()
    batch = models.CharField(max_length=10)
    password = models.CharField(max_length=256)

class Profile(models.Model):
    naem =  models.CharField(max_length=35)
    UserName = models.CharField(max_length=35)
    mobile = models.CharField(max_length = 35)
    reg_num = models.CharField(max_length = 35)
    batch = models.CharField(max_length=10)

class Balance(models.Model):
    AvBalance = models.IntegerField()
    ConsBalance = models.IntegerField()
    reg = models.CharField(max_length = 35)
    date = models.DateTimeField(auto_created=True)

class Details(models.Model):
    reg = models.CharField(max_length = 35)
    DaT = models.DateField(auto_now_add=True)
    reason = models.CharField(max_length = 256)

class RequestaRgWi(models.Model):
    Ammount = models.IntegerField()
    Reg = models.CharField(max_length = 35)
    Mobile = models.CharField(max_length=15)
    TypeOf = models.CharField(max_length = 256)