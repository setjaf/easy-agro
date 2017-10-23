#R!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

urlpatterns=[
    url(r'^nueva/(?P<prodc_id>[0-9a-z-]+)$', views.nuevaCorrida, name='nuevaCorrida'),
    url(r'^nueva/$', views.nuevaCorrida, name='nuevaCorrida'),

    #url(r'^otra/$',views.otra,name='otra')
]
