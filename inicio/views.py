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
from django.forms import formset_factory, inlineformset_factory, modelformset_factory
from django.conf import settings

from .form import NuevaRecepcion, NuevaCaja, NuevaPrueba, filtroProductor, NuevaCorrida, Multiforms, NuevoEmpleado
from .models import ProductoCampo, Caja, Empleado, Productor, Caja, Prueba, Usuario, Status_pc
import json

__VERSION = 1.0

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
                   'personal': request.user.is_personal, 'pc': 'pc',
                   'version': __VERSION,}
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
                #e = Empleado.objects.get(usuario=request.user)
                #pc = ProductoCampo.objects.filter(Empleado=e).exclude(status='t')
                p = Empleado.objects.get(usuario=request.user.id)
                context = {'nombre': p.nombre, 'admin': request.user.is_admin,
                           'personal': request.user.is_personal, 'pc': 'pc', 'version': __VERSION,}
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


def nuevaCorrida(request, prodc_id=False):
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

        empleado=Empleado.objects.get(usuario=request.user)
        recepciones=ProductoCampo.objects.all().filter(Empleado=empleado).order_by('fecha_recepcion')
        recepcionesLista=list()
        for recepcion in recepciones:
            status=Status_pc.objects.filter(IDProductoCampo=recepcion).order_by('fecha').last()
            if status.estado=='c' or status.estado=='a':
                recepcionesLista.append((recepcion.IDProductoCampo,recepcion))

        recepcionesLista.insert(0, ("---------", "---------"))
        form['corrida'].fields["ProductoCampo"].choices = recepcionesLista
        if prodc_id:
            #print dir(form['corrida'].fields["ProductoCampo"])
            form['corrida'].fields["ProductoCampo"].initial = ProductoCampo.objects.get(pk=prodc_id)
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
            if form.is_valid():
                corrida = form['corrida'].save()
                status = form['status'].save(commit=False)
                status.IDProductoCorrida = corrida
                status.save()
                return redirect('/')


            if ("localidad" in request.POST) and ("municipio" in request.POST):
                if request.POST['localidad'] == '---------' and request.POST['municipio'] != '---------':
                    productores = Productor.objects.filter(
                        municipio=request.POST['municipio'])
                elif request.POST['municipio'] == '---------' and request.POST['localidad'] != '---------':
                    productores = Productor.objects.filter(
                        localidad=request.POST['localidad'])
                elif request.POST['municipio'] != '---------' and request.POST['localidad'] != '---------':
                    productores = Productor.objects.filter(
                        localidad=request.POST['localidad'], municipio=request.POST['municipio'])
                else:
                    productores = Productor.objects.all()
                recepcionesLista=list()
                empleado=Empleado.objects.get(usuario=request.user)
                for productor in productores:
                    recepciones=ProductoCampo.objects.all().filter(Empleado=empleado,Productor=productor).order_by('fecha_recepcion')
                    for recepcion in recepciones:
                        status=Status_pc.objects.filter(IDProductoCampo=recepcion).order_by('fecha').last()
                        if status.estado=='c' or status.estado=='a':
                            recepcionesLista.append((recepcion.IDProductoCampo,recepcion))
                recepcionesLista.insert(0, ("---------", "---------"))
                form['corrida'].fields["ProductoCampo"].choices = recepcionesLista
                #form.fields["ProductoCampo"].queryset = pg.exclude(status='t')
                form1.fields["localidad"].initial = request.POST['localidad']
                form1.fields["municipio"].initial = request.POST['municipio']

        context = {'message': message, 'form': form,
                   'form1': form1, 'admin': request.user.is_admin}
        return HttpResponse(render(request, 'inicio/corrida.html', context))

    return redirect('/')


def nuevaRecepcion(request):
    if request.user.is_authenticated:
        form = NuevaRecepcion()
        form2 = filtroProductor()
        nuevacaja1=Multiforms(prefix='1')
        nuevacaja2=Multiforms(prefix='2')
        nuevacaja3=Multiforms(prefix='3')
        numcajas=1
        cajas=[nuevacaja1,nuevacaja2,nuevacaja3]
        choices = [(o, o) for o in Productor.objects.values_list(
            'localidad', flat=True).distinct()]
        choices.insert(0, ("---------", "---------"))
        form2.fields["localidad"].choices = choices
        choices = [(o, o) for o in Productor.objects.values_list(
            'municipio', flat=True).distinct()]
        choices.insert(0, ("---------", "---------"))
        form2.fields["municipio"].choices = choices
        context={'cajas':cajas,'numcajas':numcajas,'form':form,'form1': form2}

        if request.method == 'POST':
            # Si el metodo es POST significa que quieren hacer un logout, pero revisamos que sea la información correcta con un if
            if "salir" in request.POST:
                # Si nos estan mandando la informacion correcta realizamos el proceso del logout
                logout(request)
                # Se retorna La función HttpResponse que hace el render de la página del login, con el formulario copmo parametro
                return redirect('/')
            nuevacaja1=Multiforms(request.POST,prefix='1')
            nuevacaja2=Multiforms(request.POST,prefix='2')
            nuevacaja3=Multiforms(request.POST,prefix='3')
            form = NuevaRecepcion(request.POST, request.FILES)
            cajas=[nuevacaja1,nuevacaja2,nuevacaja3]
            mensaje=''
            if 'numcajas' in request.POST:
                numcajas=int(request.POST['numcajas'])

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

            elif 'agregform' in request.POST:
                numcajas=int(request.POST['agregform'])
                if numcajas <= 2:
                    numcajas=numcajas+1

            elif 'borrarform' in request.POST:
                numcajas=int(request.POST['borrarform'])
                if numcajas >= 2:
                    numcajas=numcajas-1
            else:
                if form.is_valid():
                    recepcion=form["recepcion"].save(commit=False)
                    recepcion.Empleado = Empleado.objects.get(
                        usuario=request.user)
                    recepcion.save()
                    status=form["status"].save(commit=False)
                    status.IDProductoCampo=recepcion
                    status.save()
                    cajas_validas=0
                    for caja in cajas:
                        if caja.is_valid():
                            cajas_validas+=1

                    if cajas_validas==numcajas:
                        cajas_guardadas=[]
                        for i in range(0,numcajas):
                            caja_nueva=cajas[i].save(commit=False)
                            caja_nueva["caja"].ProductoCampo=recepcion
                            caja_nueva["caja"].save()
                            caja_nueva["prueba1"].Caja=caja_nueva["caja"]
                            caja_nueva["prueba1"].save()
                            caja_nueva["prueba2"].Caja=caja_nueva["caja"]
                            caja_nueva["prueba2"].save()
                            caja_nueva["prueba3"].Caja=caja_nueva["caja"]
                            caja_nueva["prueba3"].save()
                            mensaje='Registro exitoso'
                            context={'cajas':cajas,'numcajas':numcajas,'form':form,'form1': form2, 'mensaje': mensaje}
                            if not status.estado=='c' and not status.estado=='a':
                                return HttpResponse(render(request, 'inicio/recepcion.html',context))
                            else:
                                return redirect('/corrida/nueva/'+str(recepcion.IDProductoCampo))
                    else:
                        mensaje="Por favor llena todos los datos de las cajas"
                else:
                    mensaje="Por favor llena todos los campos"
            context={'cajas':cajas,'numcajas':numcajas,'form':form,'form1': form2, 'mensaje': mensaje}

        return HttpResponse(render(request, 'inicio/recepcion.html',context))

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
                recepcion = ProductoCampo.objects.get(IDProductoCampo=prodc_id)
                recepcion.calidad_aprox = request.POST['recepcion-calidad_aprox']
                recepcion.representante = request.POST['recepcion-representante']
                if "firma" in request.FILES:
                    recepcion.firma = request.FILES['firma']
                recepcion.save()
                status=Status_pc.objects.filter(IDProductoCampo=recepcion).order_by('fecha').last()
                if not status.estado==request.POST['status-estado']:
                    status=Status_pc(IDProductoCampo=recepcion, estado=request.POST['status-estado'])
                    status.save()
                recepcion = ProductoCampo.objects.get(IDProductoCampo=prodc_id)
                status = Status_pc.objects.filter(IDProductoCampo=recepcion).order_by('fecha').last()
                form = NuevaRecepcion(instance={
                    'recepcion':recepcion,
                    'status': status
                })
                print status.estado
                if not status.estado=='c' and not status.estado=='a':
                    context = {'form': form}
                    return HttpResponse(render(request, 'inicio/recepcionMod.html', context))
                else:
                    return redirect('/corrida/nueva/'+str(recepcion.IDProductoCampo))

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
    form = NuevaRecepcion()
    form2 = filtroProductor()
    nuevacaja1=Multiforms(prefix='1')
    nuevacaja2=Multiforms(prefix='2')
    nuevacaja3=Multiforms(prefix='3')
    numcajas=1
    cajas=[nuevacaja1,nuevacaja2,nuevacaja3]
    choices = [(o, o) for o in Productor.objects.values_list(
        'localidad', flat=True).distinct()]
    choices.insert(0, ("---------", "---------"))
    form2.fields["localidad"].choices = choices
    choices = [(o, o) for o in Productor.objects.values_list(
        'municipio', flat=True).distinct()]
    choices.insert(0, ("---------", "---------"))
    form2.fields["municipio"].choices = choices
    context={'cajas':cajas,'numcajas':numcajas,'form':form,'form1': form2}

    if request.method == 'POST':
        nuevacaja1=Multiforms(request.POST,prefix='1')
        nuevacaja2=Multiforms(request.POST,prefix='2')
        nuevacaja3=Multiforms(request.POST,prefix='3')
        form = NuevaRecepcion(request.POST, request.FILES)
        cajas=[nuevacaja1,nuevacaja2,nuevacaja3]
        mensaje=''
        if 'numcajas' in request.POST:
            numcajas=int(request.POST['numcajas'])

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

        elif 'agregform' in request.POST:
            numcajas=int(request.POST['agregform'])
            if numcajas <= 2:
                numcajas=numcajas+1

        elif 'borrarform' in request.POST:
            numcajas=int(request.POST['borrarform'])
            if numcajas >= 2:
                numcajas=numcajas-1
        else:
            if form.is_valid():
                recepcion=form["recepcion"].save(commit=False)
                recepcion.Empleado = Empleado.objects.get(
                    usuario=request.user)
                recepcion.save()
                status=form["status"].save(commit=False)
                status.IDProductoCampo=recepcion
                status.save()
                cajas_validas=0
                for caja in cajas:
                    if caja.is_valid():
                        cajas_validas+=1

                if cajas_validas==numcajas:
                    cajas_guardadas=[]
                    for i in range(0,numcajas):
                        caja_nueva=cajas[i].save(commit=False)
                        caja_nueva["caja"].ProductoCampo=recepcion
                        caja_nueva["caja"].save()
                        caja_nueva["prueba1"].Caja=caja_nueva["caja"]
                        caja_nueva["prueba1"].save()
                        caja_nueva["prueba2"].Caja=caja_nueva["caja"]
                        caja_nueva["prueba2"].save()
                        caja_nueva["prueba3"].Caja=caja_nueva["caja"]
                        caja_nueva["prueba3"].save()
                        mensaje='Registro exitoso'
                        context={'cajas':cajas,'numcajas':numcajas,'form':form,'form1': form2, 'mensaje': mensaje}
                        if not status.estado=='c' and not status.estado=='a':
                            return HttpResponse(render(request, 'inicio/prueba.html',context))
                        else:
                            return redirect('/corrida/nueva/'+str(recepcion.IDProductoCampo))
                else:
                    mensaje="Por favor llena todos los datos de las cajas"
            else:
                mensaje="Por favor llena todos los campos"
        context={'cajas':cajas,'numcajas':numcajas,'form':form,'form1': form2, 'mensaje': mensaje}

    return HttpResponse(render(request, 'inicio/prueba.html',context))

'''
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

    '''


# Create your views here
