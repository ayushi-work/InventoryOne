from django.contrib import admin

from .models import Booking, Broker, Commission, Customer, OTPCode, Plot, Project

admin.site.register(Broker)
admin.site.register(OTPCode)
admin.site.register(Project)
admin.site.register(Plot)
admin.site.register(Customer)
admin.site.register(Booking)
admin.site.register(Commission)