from django.contrib import admin
from web_app import models as m
# Register your models here.

admin.site.register(m.Product)
admin.site.register(m.ProductType)