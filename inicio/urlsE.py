#R!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import viewsAdmin

urlpatterns=[
    url(r'^nuevo/$', viewsAdmin.nuevoEmpleado, name='nuevoEmpleado'),
    #url(r'^otra/$',views.otra,name='otra')
]
