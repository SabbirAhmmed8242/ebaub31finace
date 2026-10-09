from django.contrib import admin
from . models import Reg_Log_information,Profile,Balance,RequestaRgWi,Details

admin.site.register(Reg_Log_information)
admin.site.register(Details)
admin.site.register(Profile)
admin.site.register(Balance)
admin.site.register(RequestaRgWi)
# Register your models here.
