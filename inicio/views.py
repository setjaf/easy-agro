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
        empleado = Empleado.objects.get(usuario=request.user.id)
        recepciones=ProductoCampo.objects.all().filter(Empleado=empleado).order_by('fecha_recepcion')
        recepcionesLista=[]
        for recepcion in recepciones:
            status=Status_pc.objects.filter(IDProductoCampo=recepcion).order_by('fecha').last()

            if not status.estado=='c' and not status.estado=='a':
                diccionarioRecepcion={
                    'fecha':recepcion.fecha_recepcion.strftime('%d/%m/%Y'),
                    'productor':recepcion.Productor,
                    'idproducto':recepcion.IDProductoCampo
                }
                diccionarioEstado={'status':status.estado}
                diccionarioRecepcion.update(diccionarioEstado)
                recepcionesLista.append(diccionarioRecepcion)
        context = {'nombre': empleado.nombre, 'admin': request.user.is_admin,
                   'personal': request.user.is_personal, 'recepciones': recepcionesLista}
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
                empleado = Empleado.objects.get(usuario=request.user.id)
                # Ahora en el contexto se agrega un diccionario que contiene la información del usuario autentificado
                recepciones=ProductoCampo.objects.all().filter(Empleado=empleado).order_by('fecha_recepcion')
                recepcionesLista=[]
                for recepcion in recepciones:
                    status=Status_pc.objects.filter(IDProductoCampo=recepcion).order_by('fecha').last()
                    if not status.estado=='c' and not status.estado=='a':
                        diccionarioRecepcion={
                            'fecha':recepcion.fecha_recepcion.strftime('%d/%m/%Y'),
                            'productor':recepcion.Productor,
                            'idproducto':recepcion.IDProductoCampo
                        }
                        diccionarioEstado={'status':status.estado}
                        diccionarioRecepcion.update(diccionarioEstado)
                        recepcionesLista.append(diccionarioRecepcion)
                context = {'nombre': empleado.nombre, 'admin': request.user.is_admin,
                           'personal': request.user.is_personal, 'recepciones': recepcionesLista}
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
                    if not forms.is_valid() or not forms['caja'].is_valid():
                        context = {'forms': formset, 'form': form,
                                   'form1': form2, 'nforms': numform,
                                   'mensaje': 'Llena toda la información de las cajas para poder continuar'}
                        return HttpResponse(render(request, 'inicio/recepcion.html', context))
                    for formp in forms:
                        if formp.data=='' or formp.data=='0' or formp.data==0:
                            context = {'forms': formset, 'form': form,
                                       'form1': form2, 'nforms': numform,
                                       'mensaje': 'Recuerda que no se pueden registrar las cajas si dejas campos vacios o con datos en 0'}
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
        empleado=Empleado.objects.get(usuario=request.user)
        recepciones=ProductoCampo.objects.all().filter(Empleado=empleado).order_by('fecha_recepcion')
        recepcionesLista=[]
        for recepcion in recepciones:
            status=Status_pc.objects.filter(IDProductoCampo=recepcion).order_by('fecha').last()
            diccionarioRecepcion={
                'fecha':recepcion.fecha_recepcion.strftime('%d/%m/%Y'),
                'productor':recepcion.Productor,
                'idproducto':recepcion.IDProductoCampo
            }
            diccionarioEstado={'status':status.estado}
            diccionarioRecepcion.update(diccionarioEstado)
            recepcionesLista.append(diccionarioRecepcion)
        context={'recepciones':recepcionesLista, 'admin': request.user.is_admin}
        return HttpResponse(render(request, 'inicio/recepcionLista.html',context))
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
            if "borrar" in request.POST:
                p=ProductoCampo.objects.get(pk=prodc_id)
                p.delete()
                return redirect('/recepcion')
            # Inicia proceso de registro de recepción
            form = NuevaRecepcion(request.POST, request.FILES)
            if form.is_valid():
                p = ProductoCampo.objects.get(IDProductoCampo=prodc_id)
                p.calidad_aprox = request.POST['recepcion-calidad_aprox']
                p.representante = request.POST['recepcion-representante']
                if "firma" in request.FILES:
                    p.firma = request.FILES['firma']
                p.save()
                status=Status_pc.objects.filter(IDProductoCampo=p).order_by('fecha').last()
                if not status.estado==request.POST['status-estado']:
                    status=Status_pc(IDProductoCampo=p, estado=request.POST['status-estado'])
                    status.save()
                pc = ProductoCampo.objects.get(IDProductoCampo=prodc_id)
                status = Status_pc.objects.filter(IDProductoCampo=pc).order_by('fecha').last()
                form = NuevaRecepcion(instance={
                    'recepcion':pc,
                    'status': status
                })
                context = {'form': form}
                return HttpResponse(render(request, 'inicio/recepcionMod.html', context))
                #return redirect('/recepcion')
        pc = ProductoCampo.objects.get(IDProductoCampo=prodc_id)
        status = Status_pc.objects.filter(IDProductoCampo=pc).order_by('fecha').last()
        form = NuevaRecepcion(instance={
            'recepcion':pc,
            'status': status
        })
        context = {'form': form}
        return HttpResponse(render(request, 'inicio/recepcionMod.html', context))

    return redirect('/')


def prueba(request):
    empleado=Empleado.objects.get(usuario=request.user)
    recepciones=ProductoCampo.objects.all().filter(Empleado=empleado).order_by('fecha_recepcion')
    recepcionesLista=[]
    for recepcion in recepciones:
        status=Status_pc.objects.filter(IDProductoCampo=recepcion).order_by('fecha').last()
        if not status.estado=='c' and not status.estado=='a':
            diccionarioRecepcion={
                'fecha':recepcion.fecha_recepcion.strftime('%d/%m/%Y'),
                'productor':recepcion.Productor,
                'idproducto':recepcion.IDProductoCampo
            }
            diccionarioEstado={'status':status.estado}
            diccionarioRecepcion.update(diccionarioEstado)
            recepcionesLista.append(diccionarioRecepcion)
    context={'recepciones':recepcionesLista}
    return HttpResponse(render(request, 'inicio/prueba.html',context))

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
