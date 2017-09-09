#R!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

urlpatterns=[
    url(r'^nueva/$', views.nuevaCorrida, name='nuevaCorrida'),
    #url(r'^otra/$',views.otra,name='otra')
]
