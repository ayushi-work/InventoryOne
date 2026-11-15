from django.contrib import admin

from .models import Broker, OTPCode, Plot, Project

admin.site.register(Broker)
admin.site.register(OTPCode)
admin.site.register(Project)
admin.site.register(Plot)
