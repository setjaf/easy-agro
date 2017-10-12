# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.utils import timezone
import datetime
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template import RequestContext, loader
from inicio.form import LoginForm
from django.contrib.auth import authenticate, login, logout
from django.forms.models import model_to_dict
from django.forms import formset_factory
from django.conf import settings

from .form import MultiEmUs
from .models import ProductoCampo, Caja, Empleado, Productor, Caja, Prueba, Usuario
import json


def nuevoEmpleado(request):

    if request.user.is_authenticated and request.user.is_admin:
        if request.method == "POST":
            form = MultiEmUs(request.POST)
            form.is_valid()
            e=form.save(commit=False)
        form = MultiEmUs()
        context={'form':form}
        return HttpResponse(render(request, 'inicio/empleadoNuevo.html', context))

    pass
