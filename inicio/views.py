# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.utils import timezone
import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext, loader
from inicio.form import LoginForm
from django.contrib.auth import authenticate, login, logout
from django.forms.models import model_to_dict
from django.forms import formset_factory
from django.conf import settings

from .form import NuevaRecepcion, NuevaCaja, NuevaPrueba, filtroProductor, NuevaCorrida, Multiforms, NuevoEmpleado
from .models import ProductoCampo, Caja, Empleado, Productor, Caja, Prueba, Usuario, Status_pc
import json


def index(request):
    # Se inicializa la variable mensaje con None para  no mostrar mensaje el la primera petición
    message = ""
    # Inicializamos la variable "form" con un form vacio
    form = LoginForm()
    # Verificamos si el usuario al hacer el request está autentificado
    if request.user.is_authenticated:
        # Se verifica si el metodo de envio fue post
        if request.method == "POST":
            # Si el metodo es POST significa que quieren hacer un logout, pero revisamos que sea la información correcta con un if
            if "salir" in request.POST:
                # Si nos estan mandando la informacion correcta realizamos el proceso del logout
                logout(request)
                # Damos valor a la variable context y le mandamos el form vacio que inicializamos
                context = {'form': form}
                # Se retorna La función HttpResponse que hace el render de la página del login, con el formulario copmo parametro
                return HttpResponse(render(request, 'inicio/login.html', context))
        # Si el metodo no es POST, nos indica que debemos renderizar la página inicial de un usario autentificado, obtenemos la informacion del objeto Personal
        p = Empleado.objects.get(usuario=request.user.id)
        # Ahora en el contexto se agrega un diccionario que contiene la información del usuario autentificado
        #e = Empleado.objects.get(usuario=request.user)
        #pc = ProductoCampo.objects.filter(Empleado=e).exclude(status='t')
        context = {'nombre': p.nombre, 'admin': request.user.is_admin,
                   'personal': request.user.is_personal, 'pc': 'pc'}
        # Por último regresamos la función HttpResponse, que hace el render del template inicio con la información del personal
        if request.user.is_admin:
            return HttpResponse(render(request, 'inicio/inicioAdmin.html', context))
        else:
            return HttpResponse(render(request, 'inicio/inicio.html', context))
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                message = 'Te has autentificado correctamente'
                p = Empleado.objects.get(usuario=request.user.id)
                # Ahora en el contexto se agrega un diccionario que contiene la información del usuario autentificado
                #e = Empleado.objects.get(usuario=request.user)
                #pc = ProductoCampo.objects.filter(Empleado=e).exclude(status='t')
                context = {'nombre': p.nombre, 'admin': request.user.is_admin,
                           'personal': request.user.is_personal, 'pc': 'pc'}
                # Por último regresamos la función HttpResponse, que hace el render del template inicio con la información del personal
                if request.user.is_admin:
                    return HttpResponse(render(request, 'inicio/inicioAdmin.html', context))
                else:
                    return HttpResponse(render(request, 'inicio/inicio.html', context))
            else:
                message = 'Usuario o contraseña erróneos.'
        else:
            message = 'Introduce tus datos.'
    else:
        form = LoginForm()

    context = {'message': message, 'form': form}
    return HttpResponse(render(request, 'inicio/login.html', context))


def nuevaCorrida(request):
    if request.user.is_authenticated:
        message = None
        form1 = filtroProductor()
        choices = [(o, o) for o in Productor.objects.values_list(
            'localidad', flat=True).distinct()]
        choices.insert(0, ("---------", "---------"))
        form1.fields["localidad"].choices = choices
        choices = [(o, o) for o in Productor.objects.values_list(
            'municipio', flat=True).distinct()]
        choices.insert(0, ("---------", "---------"))
        form1.fields["municipio"].choices = choices

        form = NuevaCorrida()
        #form.fields['fecha_compra'].widget.attrs['class'] = 'datepicker'
        form.fields['ProductoCampo'].queryset = ProductoCampo.objects.exclude(
            status='t')
        # Se verifica si el metodo de envio fue post
        if request.method == "POST":
            # Si el metodo es POST significa que quieren hacer un logout, pero revisamos que sea la información correcta con un if
            if "salir" in request.POST:
                # Si nos estan mandando la informacion correcta realizamos el proceso del logout
                logout(request)
                # Se retorna La función HttpResponse que hace el render de la página del login, con el formulario copmo parametro
                return redirect('/')

            # Inicia proceso de registro de recepción
            form = NuevaCorrida(request.POST)
            # if form.is_valid():
            #    form.save()
            #    return redirect('/')

            form.fields['fecha_compra'].widget.attrs['class'] = 'datepicker'

            if ("localidad" in request.POST) and ("municipio" in request.POST):
                if request.POST['localidad'] == '---------' and request.POST['municipio'] != '---------':
                    prod = Productor.objects.filter(
                        municipio=request.POST['municipio'])
                elif request.POST['municipio'] == '---------' and request.POST['localidad'] != '---------':
                    prod = Productor.objects.filter(
                        localidad=request.POST['localidad'])
                elif request.POST['municipio'] != '---------' and request.POST['localidad'] != '---------':
                    prod = Productor.objects.filter(
                        localidad=request.POST['localidad'], municipio=request.POST['municipio'])
                else:
                    prod = Productor.objects.all()
                lpc = []
                for p in prod:
                    pc = ProductoCampo.objects.filter(Productor=p)
                    if pc and pc[0].status != 't':
                        lpc.append((pc[0].IDProductoCampo, pc[0]))
                lpc.insert(0, ("---------", "---------"))
                form['corrida'].fields["ProductoCampo"].choices = lpc
                #form.fields["ProductoCampo"].queryset = pg.exclude(status='t')
                form1.fields["localidad"].initial = request.POST['localidad']
                form1.fields["municipio"].initial = request.POST['municipio']
        base = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base, 'static/datos/calibres.json'), "r+") as json_data:
            d = json.load(json_data)
            # print d
            json_data.close()
            calibres = [(key, d[key])for key in d]
            calibres.insert(0, ("---------", "---------"))
            '''print calibres
            d.update({"prueba":"prueba"})'''
            calibres.sort()
        form['corrida'].fields["calibre"].choices = calibres
        context = {'message': message, 'form': form,
                   'form1': form1, 'admin': request.user.is_admin}
        return HttpResponse(render(request, 'inicio/corrida.html', context))

    return redirect('/')


def nuevaRecepcion(request):
    if request.user.is_authenticated:
        #----------------------------------------------------------
        message = None
        form = NuevaRecepcion()
        form2 = filtroProductor()
        choices = [(o, o) for o in Productor.objects.values_list(
            'localidad', flat=True).distinct()]
        choices.insert(0, ("---------", "---------"))
        form2.fields["localidad"].choices = choices
        choices = [(o, o) for o in Productor.objects.values_list(
            'municipio', flat=True).distinct()]
        choices.insert(0, ("---------", "---------"))
        form2.fields["municipio"].choices = choices
        # Inicia proceso de registro de recepción
        #----------------------------------------------------------
        numform = 1
        multiformset = formset_factory(Multiforms, extra=numform, max_num=3)
        if request.method == 'POST':
            if "salir" in request.POST:
                # Si nos estan mandando la informacion correcta realizamos el proceso del logout
                logout(request)
                # Se retorna La función HttpResponse que hace el render de la página del login, con el formulario copmo parametro
                return redirect('/')
            numform = int(request.POST["numform"])
            multiformset = formset_factory(
                Multiforms, extra=numform, max_num=3)

            if ("localidad" in request.POST) and ("municipio" in request.POST):

                if request.POST['localidad'] == '---------':
                    form['recepcion'].fields["Productor"].queryset = Productor.objects.filter(
                        municipio=request.POST['municipio'])
                elif request.POST['municipio'] == '---------':
                    form['recepcion'].fields["Productor"].queryset = Productor.objects.filter(
                        localidad=request.POST['localidad'])
                else:
                    form['recepcion'].fields["Productor"].queryset = Productor.objects.filter(
                        localidad=request.POST['localidad'], municipio=request.POST['municipio'])
                form2.fields["localidad"].initial = request.POST['localidad']
                form2.fields["municipio"].initial = request.POST['municipio']
                multiformset = formset_factory(
                    Multiforms, extra=numform, max_num=3)
                data = {
                    'form-TOTAL_FORMS': multiformset().total_form_count(),
                    'form-INITIAL_FORMS': multiformset().initial_form_count(),
                    'form-MAX_NUM_FORMS': '3',
                }

                data.update(request.POST.dict())
                formset = multiformset(data)
            elif 'agregform' in request.POST:
                if not request.POST['agregform'] == '3':
                    numform = int(request.POST['agregform']) + 1
                multiformset = formset_factory(
                    Multiforms, extra=numform, max_num=3)
                data = {
                    'form-TOTAL_FORMS': multiformset().total_form_count(),
                    'form-INITIAL_FORMS': multiformset().initial_form_count(),
                    'form-MAX_NUM_FORMS': '3',
                }
                form = NuevaRecepcion(request.POST, request.FILES)
                data.update(request.POST.dict())
                formset = multiformset(data)
            elif 'borrarform' in request.POST:
                if not request.POST['borrarform'] == '1':
                    numform = int(request.POST['borrarform']) - 1
                multiformset = formset_factory(
                    Multiforms, extra=numform, max_num=3)
                data = {
                    'form-TOTAL_FORMS': multiformset().total_form_count(),
                    'form-INITIAL_FORMS': multiformset().initial_form_count(),
                    'form-MAX_NUM_FORMS': '3',
                }
                form = NuevaRecepcion(request.POST, request.FILES)
                data.update(request.POST.dict())
                formset = multiformset(data)

            else:

                data = {
                    'form-TOTAL_FORMS': multiformset().total_form_count(),
                    'form-INITIAL_FORMS': multiformset().initial_form_count(),
                    'form-MAX_NUM_FORMS': '3',
                }

                data.update(request.POST.dict())
                formset = multiformset(data)
                form = NuevaRecepcion(request.POST, request.FILES)

                for forms in formset:
                    if not forms.is_valid():
                        context = {'forms': formset, 'form': form, 'form1': form2, 'nforms': numform,
                                   'mensaje': 'Llena toda la información de las cajas para poder continuar'}
                        return HttpResponse(render(request, 'inicio/recepcion.html', context))

                if form.is_valid():
                    recepcion = form['recepcion'].save(commit=False)
                    recepcion.Empleado = Empleado.objects.get(
                        usuario=request.user)
                    recepcion.save()
                    status = form['status'].save(commit=False)
                    status.IDProductoCampo = recepcion
                    status.save()
                    if "firma" in request.FILES:
                        recepcion.firma = request.FILES['firma']
                        recepcion.save(commit=False)

                for forms in formset:
                    if forms.is_valid():
                        c = forms['caja'].save(commit=False)
                        c.ProductoCampo = recepcion
                        c.save()
                        p1 = forms['prueba1'].save(commit=False)
                        p1.Caja = c
                        p1.save()
                        p2 = forms['prueba2'].save(commit=False)
                        p2.Caja = c
                        p2.save()
                        p3 = forms['prueba3'].save(commit=False)
                        p3.Caja = c
                        p3.save()
                        print c
                        print p1
                        print p2
                        print p3

                context = {'forms': formset, 'form': form, 'form1': form2,
                           'nforms': numform, 'mensaje': 'Registro exitoso'}
                return HttpResponse(render(request, 'inicio/recepcion.html', context))
                '''if form.is_valid():
                    m=form.save(commit=False)
                    print m'''
            print dir(formset)
            print formset.validate_max
            context = {'forms': formset, 'form': form,
                       'form1': form2, 'nforms': numform}
            return HttpResponse(render(request, 'inicio/recepcion.html', context))
        '''for form in multiformset():
            print(form)'''
        context = {'forms': multiformset, 'form': form,
                   'form1': form2, 'nforms': numform}
        return HttpResponse(render(request, 'inicio/recepcion.html', context))

    return redirect('/')


def listaRecepcion(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            # Si el metodo es POST significa que quieren hacer un logout, pero revisamos que sea la información correcta con un if
            if "salir" in request.POST:
                # Si nos estan mandando la informacion correcta realizamos el proceso del logout
                logout(request)
                # Se retorna La función HttpResponse que hace el render de la página del login, con el formulario copmo parametro
                return redirect('/')
        e = Empleado.objects.get(usuario=request.user)
        pc = ProductoCampo.objects.filter(Empleado=e)
        context = {'pc': pc}
        return HttpResponse(render(request, 'inicio/recepcionLista.html', context))
    return redirect('/')


def modRecepcion(request, prodc_id):
    if request.user.is_authenticated:
        form = NuevaRecepcion()
        # Se verifica si el metodo de envio fue post
        if request.method == "POST":
            # Si el metodo es POST significa que quieren hacer un logout, pero revisamos que sea la información correcta con un if
            if "salir" in request.POST:
                # Si nos estan mandando la informacion correcta realizamos el proceso del logout
                logout(request)
                # Se retorna La función HttpResponse que hace el render de la página del login, con el formulario copmo parametro
                return redirect('/')

            # Inicia proceso de registro de recepción
            form = NuevaRecepcion(request.POST, request.FILES)
            if form.is_valid():
                p = ProductoCampo.objects.get(IDProductoCampo=prodc_id)
                p.calidad_aprox = request.POST['calidad_aprox']
                p.status = request.POST['status']
                p.representante = request.POST['representante']
                p.Empleado = Empleado.objects.get(usuario=request.user.id)

                if "firma" in request.FILES:
                    p.firma = request.FILES['firma']
                p.save()
                return redirect('/recepcion')
        pc = ProductoCampo.objects.get(IDProductoCampo=prodc_id)
        form = NuevaRecepcion(model_to_dict(pc))
        context = {'form': form}
        return HttpResponse(render(request, 'inicio/recepcionMod.html', context))

    return redirect('/')


def prueba(request):
<<<<<<< HEAD
    recepciones=ProductoCampo.objects.all()
    for recepcion in recepciones:
        status=Status_pc.objects.filter(IDProductoCampo=recepcion).exclude(estado=['c','a']).order_by('fecha').first()
        print status.estado
        print status.fecha
    return HttpResponse(render(request, 'inicio/prueba.html'))
=======
    u = Usuario.objects.create_user('Dante', 'nte111da@gmail.com', 'prueba')
    u.save()
    return redirect('/')


>>>>>>> 4ec84e32fb5c32fe1c63ae68afccc9bf8cba37fa
'''
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, 'static/datos/calibres.json'),"r+") as json_data:
        d = json.load(json_data)
        #print d
        json_data.close()
        calibres=[(key,d[key])for key in d]
        print calibres
        d.update({"prueba":"prueba"})

    with open(os.path.join(base, 'static/datos/calibres.json'),"w+") as json_data:
        d=json.dumps(d)
        json_data.write(d)
        json_data.close()

    if request.user.is_authenticated:
        #----------------------------------------------------------
        message=None;
        form = NuevaRecepcion()
        form2 = filtroProductor()
        choices = [(o,o) for o in Productor.objects.values_list('localidad', flat=True).distinct()]
        choices.insert(0, ("---------","---------"))
        form2.fields["localidad"].choices = choices
        choices = [(o,o) for o in Productor.objects.values_list('municipio', flat=True).distinct()]
        choices.insert(0, ("---------","---------"))
        form2.fields["municipio"].choices = choices
        #Se verifica si el metodo de envio fue post
        if request.method == "POST":
            #Si el metodo es POST significa que quieren hacer un logout, pero revisamos que sea la información correcta con un if
            if "salir" in request.POST:
                #Si nos estan mandando la informacion correcta realizamos el proceso del logout
                logout(request)
                #Se retorna La función HttpResponse que hace el render de la página del login, con el formulario copmo parametro
                return redirect('/')
        #----------------------------------------------------------
        numform=1
        multiformset = formset_factory(Multiforms, extra=numform, max_num=3)
        if request.method=='POST':

            if ("localidad" in request.POST) and ("municipio" in request.POST):
                if request.POST['localidad']=='---------':
                    form['recepcion'].fields["Productor"].queryset = Productor.objects.filter(municipio=request.POST['municipio'])
                elif request.POST['municipio']=='---------':
                    form['recepcion'].fields["Productor"].queryset = Productor.objects.filter(localidad=request.POST['localidad'])
                else:
                    form['recepcion'].fields["Productor"].queryset = Productor.objects.filter(localidad=request.POST['localidad'],municipio=request.POST['municipio'])
                form2.fields["localidad"].initial=request.POST['localidad']
                form2.fields["municipio"].initial=request.POST['municipio']
                multiformset = formset_factory(Multiforms, extra=numform, max_num=3)
                data = {
                    'form-TOTAL_FORMS': multiformset().total_form_count(),
                    'form-INITIAL_FORMS': multiformset().initial_form_count(),
                    'form-MAX_NUM_FORMS': '3',
                }

                data.update(request.POST.dict())
                formset = multiformset(data)
            elif 'agregform' in request.POST:
                if not request.POST['agregform']=='3':
                    numform=int(request.POST['agregform'])+1
                multiformset = formset_factory(Multiforms, extra=numform, max_num=3)
                data = {
                    'form-TOTAL_FORMS': multiformset().total_form_count(),
                    'form-INITIAL_FORMS': multiformset().initial_form_count(),
                    'form-MAX_NUM_FORMS': '3',
                }

                data.update(request.POST.dict())
                formset = multiformset(data)
            elif 'borrarform' in request.POST:
                if not request.POST['borrarform']=='1':
                    numform=int(request.POST['borrarform'])-1
                multiformset = formset_factory(Multiforms, extra=numform, max_num=3)
                data = {
                    'form-TOTAL_FORMS': multiformset().total_form_count(),
                    'form-INITIAL_FORMS': multiformset().initial_form_count(),
                    'form-MAX_NUM_FORMS': '3',
                }

                data.update(request.POST.dict())
                formset = multiformset(data)

            else:
                data = {
                    'form-TOTAL_FORMS': multiformset().total_form_count(),
                    'form-INITIAL_FORMS': multiformset().initial_form_count(),
                    'form-MAX_NUM_FORMS': '3',
                }

                data.update(request.POST.dict())
                formset = multiformset(data)
                form = NuevaRecepcion(request.POST, request.FILES)
                if form.is_valid():
                    recepcion = form['recepcion'].save(commit=False)
                    recepcion.Empleado = Empleado.objects.get(usuario=request.user)
                    recepcion.save()
                    status = form['status'].save(commit=False)
                    status.IDProductoCampo = recepcion
                    status.save()
                    if "firma" in request.FILES:
                        recepcion.firma=request.FILES['firma']
                        recepcion.save(commit=False)

                for forms in formset:
                    if forms.is_valid():
                        p=forms.save(commit=False)
                        print p

                    if form.is_valid():
                        m=form.save(commit=False)
                        print m

            context={'forms':formset,'form':form,'form1':form2,'nforms':numform}
            return HttpResponse(render(request, 'inicio/prueba.html', context))
        for form in multiformset():
            print(form)
        context={'forms':multiformset,'form':form,'form1':form2,'nforms':numform}
        return HttpResponse(render(request, 'inicio/prueba.html', context))'''


# Create your views here
