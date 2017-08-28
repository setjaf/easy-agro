# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Productor, ProductoCampo, Huerto, Empleado

admin.site.register(Productor)
admin.site.register(ProductoCampo)
admin.site.register(Huerto)
admin.site.register(Empleado)

# Register your models here.
