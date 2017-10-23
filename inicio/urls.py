#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

urlpatterns=[
    url(r'^$', views.index, name='index'),
    url(r'^prueba/$', views.prueba, name='prueba')
    #url(r'^otra/$',views.otra,name='otra')
]
