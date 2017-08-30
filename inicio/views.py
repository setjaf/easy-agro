# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
import datetime
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template import RequestContext, loader

from inicio.form import NuevaRecepcion, NuevaCaja
from .models import ProductoCampo, Caja

def nuevaRecepcion(request):
    message=None;
    form = NuevaRecepcion()
    form1 = NuevaCaja
    if request.method == "POST":
        form = NuevaRecepcion(request.POST, request.FILES)
        form1 = NuevaCaja(request.POST)
        if form.is_valid():
            #m=form.save()
            #m.fecha_recepcion=datetime.datetime.now()
            #m.save()
            context={'message':message, 'form':form1}
            return HttpResponse(render(request, 'inicio/recepcionCaja.html', context))

        if form1.is_valid():
            form1=NuevaCaja()
            context={'message':message, 'form':form1}
            return HttpResponse(render(request, 'inicio/recepcionCaja.html', context))

    context={'message':message, 'form':form}
    return HttpResponse(render(request, 'inicio/recepcion.html', context))



# Create your views here.
