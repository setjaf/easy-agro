# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
import datetime
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template import RequestContext, loader
from inicio.form import LoginForm
from django.contrib.auth import authenticate, login, logout

from inicio.form import NuevaRecepcion, NuevaCaja, NuevaPrueba, filtroProductor, NuevaCorrida
from .models import ProductoCampo, Caja, Empleado, Productor, Caja, Prueba

def index(request):
    #Se inicializa la variable mensaje con None para  no mostrar mensaje el la primera petición
    message=""
    #Inicializamos la variable "form" con un form vacio
    form = LoginForm()
    #Verificamos si el usuario al hacer el request está autentificado
    if request.user.is_authenticated:
        #Se verifica si el metodo de envio fue post
        if request.method == "POST":
            #Si el metodo es POST significa que quieren hacer un logout, pero revisamos que sea la información correcta con un if
            if "salir" in request.POST:
                #Si nos estan mandando la informacion correcta realizamos el proceso del logout
                logout(request)
                #Damos valor a la variable context y le mandamos el form vacio que inicializamos
                context={'form':form}
                #Se retorna La función HttpResponse que hace el render de la página del login, con el formulario copmo parametro
                return HttpResponse(render(request, 'inicio/login.html', context))
        #Si el metodo no es POST, nos indica que debemos renderizar la página inicial de un usario autentificado, obtenemos la informacion del objeto Personal
        p=Empleado.objects.get(usuario=request.user.id)
        #Ahora en el contexto se agrega un diccionario que contiene la información del usuario autentificado
        context={'nombre':p.nombre,'admin':request.user.is_admin,'personal':request.user.is_personal}
        #Por último regresamos la función HttpResponse, que hace el render del template inicio con la información del personal
        return HttpResponse(render(request, 'inicio/inicio.html',context))

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username,password=password)
            if user is not None:
                login (request,user)
                message = 'Te has autentificado correctamente'
                p=Empleado.objects.get(usuario=request.user.id)
                #Ahora en el contexto se agrega un diccionario que contiene la información del usuario autentificado
                context={'nombre':p.nombre,'admin':request.user.is_admin,'personal':request.user.is_personal}
                #Por último regresamos la función HttpResponse, que hace el render del template inicio con la información del personal
                return HttpResponse(render(request, 'inicio/inicio.html',context))
            else:
                message = 'Usuario o contraseña erroneos'
        else:
            message = 'Introduce tus datos'
    else:
        form = LoginForm()
    context={'message':message, 'form':form}
    return HttpResponse(render(request, 'inicio/login.html', context))

def nuevaCorrida(request):
    message=None
    form1 = filtroProductor()
    choices = [(o,o) for o in Productor.objects.values_list('localidad', flat=True).distinct()]
    choices.insert(0, ("---------","---------"))
    form1.fields["localidad"].choices = choices
    choices = [(o,o) for o in Productor.objects.values_list('municipio', flat=True).distinct()]
    choices.insert(0, ("---------","---------"))
    form1.fields["municipio"].choices = choices

    form = NuevaCorrida()
    form.fields['fecha_compra'].widget.attrs['class'] = 'datepicker'
    form.fields['ProductoCampo'].queryset=ProductoCampo.objects.exclude(status='t')

    if request.user.is_authenticated:
        #Se verifica si el metodo de envio fue post
        if request.method == "POST":
            #Si el metodo es POST significa que quieren hacer un logout, pero revisamos que sea la información correcta con un if
            if "salir" in request.POST:
                #Si nos estan mandando la informacion correcta realizamos el proceso del logout
                logout(request)
                #Se retorna La función HttpResponse que hace el render de la página del login, con el formulario copmo parametro
                return redirect('/')

            #Inicia proceso de registro de recepción
            form = NuevaCorrida(request.POST)
            print(request.POST)
            print(form.is_valid())
            if form.is_valid():
                form.save()
                return redirect('/')

            form.fields['fecha_compra'].widget.attrs['class'] = 'datepicker'

            if ("localidad" in request.POST) and ("municipio" in request.POST):
                if request.POST['localidad']=='---------':
                    prod = Productor.objects.filter(municipio=request.POST['municipio'])
                elif request.POST['municipio']=='---------':
                    prod = Productor.objects.filter(localidad=request.POST['localidad'])
                else:
                    prod = Productor.objects.filter(localidad=request.POST['localidad'],municipio=request.POST['municipio'])

                lpc=[]
                for p in prod:
                    pc=ProductoCampo.objects.filter(Productor=p)
                    if pc and pc[0].status!='t':
                        lpc.append((pc[0].IDProductoCampo,pc[0]))
                lpc.insert(0, ("---------","---------"))
                form.fields["ProductoCampo"].choices = lpc
                #form.fields["ProductoCampo"].queryset = pg.exclude(status='t')
                form1.fields["localidad"].initial=request.POST['localidad']
                form1.fields["municipio"].initial=request.POST['municipio']
        context={'message':message, 'form':form, 'form1':form1}
        return HttpResponse(render(request, 'inicio/corrida.html', context))

    return redirect('/')

def nuevaRecepcion(request):
    message=None;
    form = NuevaRecepcion()
    form1 = NuevaCaja()
    form2 = filtroProductor()
    choices = [(o,o) for o in Productor.objects.values_list('localidad', flat=True).distinct()]
    choices.insert(0, ("---------","---------"))
    form2.fields["localidad"].choices = choices
    choices = [(o,o) for o in Productor.objects.values_list('municipio', flat=True).distinct()]
    choices.insert(0, ("---------","---------"))
    form2.fields["municipio"].choices = choices
    if request.user.is_authenticated:
        #Se verifica si el metodo de envio fue post
        if request.method == "POST":
            #Si el metodo es POST significa que quieren hacer un logout, pero revisamos que sea la información correcta con un if
            if "salir" in request.POST:
                #Si nos estan mandando la informacion correcta realizamos el proceso del logout
                logout(request)
                #Se retorna La función HttpResponse que hace el render de la página del login, con el formulario copmo parametro
                return redirect('/')

            #Inicia proceso de registro de recepción
            form = NuevaRecepcion(request.POST, request.FILES)
            form1 = NuevaCaja(request.POST)
            if form.is_valid():
                p=ProductoCampo(
                    calidad_aprox=request.POST['calidad_aprox'],
                    fecha_recepcion=datetime.datetime.now(),
                    status=request.POST['status'],
                    representante = request.POST['representante'],
                    Productor= Productor.objects.get(pk=request.POST['Productor']),
                    Empleado = Empleado.objects.get(usuario=request.user.id)
                )
                if "firma" in request.FILES:
                    p.firma=request.FILES['firma']
                p.save()
                context={'message':message, 'form':form1, 'recepcion':p.IDProductoCampo}
                return HttpResponse(render(request, 'inicio/recepcionCaja.html', context))

            if form1.is_valid():
                c=Caja(
                    peso_neto=request.POST['peso_neto'],
                    color=request.POST['color'],
                    cantidad=request.POST['cantidad'],
                    tamanio=request.POST['tamanio'],
                    alto=request.POST['alto'],
                    ancho=request.POST['ancho'],
                    largo=request.POST['largo'],
                    ProductoCampo=ProductoCampo.objects.get(pk=request.POST['recepcion'])
                )
                c.save()
                m=Prueba(
                    kilogramos=request.POST['kilogramos'],
                    Caja = c
                )
                m.save()
                m=Prueba(
                    kilogramos=request.POST['kilogramos1'],
                    Caja = c
                )
                m.save()
                m=Prueba(
                    kilogramos=request.POST['kilogramos2'],
                    Caja = c
                )
                m.save()
                if "sigue" in request.POST:
                    form1 = NuevaCaja()
                    context={'message':message, 'form':form1, 'recepcion':request.POST['recepcion'] }
                    return HttpResponse(render(request, 'inicio/recepcionCaja.html', context))
                return redirect('/')

            if ("localidad" in request.POST) and ("municipio" in request.POST):
                if request.POST['localidad']=='---------':
                    form.fields["Productor"].queryset = Productor.objects.filter(municipio=request.POST['municipio'])
                elif request.POST['municipio']=='---------':
                    form.fields["Productor"].queryset = Productor.objects.filter(localidad=request.POST['localidad'])
                else:
                    form.fields["Productor"].queryset = Productor.objects.filter(localidad=request.POST['localidad'],municipio=request.POST['municipio'])
                form2.fields["localidad"].initial=request.POST['localidad']
                form2.fields["municipio"].initial=request.POST['municipio']
        context={'message':message, 'form':form, 'form1':form2}
        return HttpResponse(render(request, 'inicio/recepcion.html', context))

    return redirect('/')



# Create your views here.
