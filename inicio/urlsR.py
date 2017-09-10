#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

urlpatterns=[
    url(r'^$', views.listaRecepcion, name='listaRecepcion'),
    #[0-9A-Za-z]*\w
    url(r'^nueva/$', views.nuevaRecepcion, name='nuevaRecepcion'),
    url(r'^(?P<prodc_id>[0-9a-z-]+)$', views.modRecepcion, name='modRecepcion'),
    #url(r'^otra/$',views.otra,name='otra')
]
