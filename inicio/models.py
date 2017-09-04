# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
import datetime
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from django_mysql.models import EnumField

from .managers import UserManager



class Usuario(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('username'), max_length=200,unique=True)
    email = models.EmailField(_('email address'))
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff'), default=False)
    is_admin = models.BooleanField(_('administrador'), default=False)
    is_personal = models.BooleanField(_('Personal'), default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []


    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.username

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)

# Create your models here.

class Empleado(models.Model):
    IDEmpleado = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    nombre = models.CharField(max_length=100, blank=True)
    apellido_paterno = models.CharField(max_length=100, blank=True)
    apellido_materno = models.CharField(max_length=100, blank=True)
    direccion = models.CharField(max_length=300, blank=True)
    rfc = models.CharField(max_length=13, blank=False)
    telefono = models.CharField(max_length=20, blank=True)
    puesto = models.CharField(max_length=100, blank=True)
    fecha_indusion = models.DateTimeField('dia_creado', auto_now_add=True)
    usuario = models.OneToOneField(Usuario,on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.nombre

class Productor(models.Model):
    IDProductor = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    nombre = models.CharField(max_length=100, blank=True)
    apellido_paterno = models.CharField(max_length=100, blank=True)
    apellido_materno = models.CharField(max_length=100, blank=True)
    direccion = models.CharField(max_length=100, blank=True)
    localidad = models.CharField(max_length=100, blank=True)
    municipio = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=100, blank=True)
    rfc = models.CharField(max_length=13, null=False)
    telefono = models.CharField(max_length=30, blank=True)
    fecha_inclusion = models.DateTimeField('dia_creado', auto_now_add=False)
    def __str__(self):
        return self.nombre+" - "+self.localidad


class Huerto(models.Model):
    IDHuerto = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    numero_hectareas=models.DecimalField(max_digits=10, decimal_places=3, default=0, blank=False, null=False)
    numero_tablas=models.IntegerField(blank=False,null=False)
    Productor = models.ForeignKey('Productor',on_delete=models.CASCADE, unique=False, null=False, blank=False)


class ProductoCampo(models.Model):
    IDProductoCampo = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    calidad_aprox = EnumField(choices=[('e','Excelente'), ('b','Buena'), ('r','Regular'),('m','Mala')])
    fecha_recepcion = models.DateTimeField('dia_creado',null=True)
    firma = models.ImageField(upload_to = 'pic_folder/', default = 'pic_folder/None/no-img.jpg')
    status = EnumField(choices=[('t','Terminada'), ('p','En proceso'), ('e','Entregada')])
    representante = models.CharField(max_length=100, blank=False, null=False)
    Empleado = models.ForeignKey('Empleado',on_delete=models.CASCADE, unique=False, null=False, blank=False)
    Productor = models.ForeignKey('Productor',on_delete=models.CASCADE, unique=False, null=False, blank=False)

class Producto(models.Model):
    IDProducto = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    nombre = models.CharField(max_length=100, blank=True)
    descripcion = models.CharField(max_length=300, blank=True)


class ProductoCorrida(models.Model):
    IDProductoCorrida = models.AutoField(primary_key=True, null=False)
    calibre = models.CharField(max_length=100, blank=False, null=False)
    kilogramos = models.DecimalField(max_digits=10, decimal_places=3, default=0, blank=False, null=False)
    fecha_inclusion = models.DateTimeField('dia_creado', auto_now_add=True)
    fecha_compra = models.DateTimeField('dia_creado', auto_now_add=True)
    status = EnumField(choices=[('t','Terminada'), ('p','En proceso'), ('e','Entregada')])
    folio = models.CharField(max_length=100, blank=False, null=False)
    Producto = models.ForeignKey('Producto',on_delete=models.CASCADE, unique=False, null=False, blank=False)
    ProductoCampo = models.ForeignKey('ProductoCampo',on_delete=models.CASCADE, unique=False, null=False, blank=False)
    Detalle = models.ForeignKey('Detalle',on_delete=models.CASCADE,unique=False, null=False, blank=False)


class Precio(models.Model):
    ID = models.AutoField(primary_key=True, null=False)
    datetime = models.DateTimeField('dia_creado', auto_now_add=True)
    preciokg = models.DecimalField(max_digits=10, decimal_places=3, default=0, blank=False, null=False)
    tipo = EnumField(choices=[('c','Compra'), ('v','Venta')])
    ProductoCorrida = models.ForeignKey('ProductoCorrida',on_delete=models.CASCADE, unique=False, null=False, blank=False)
    Empleado = models.ForeignKey('Empleado',on_delete=models.CASCADE, unique=False, null=False, blank=False)
    def __str__(self):
        return self.ID

class Caja(models.Model):
    ID = models.AutoField(primary_key=True, null=False)
    peso_neto = EnumField(choices=[('t','Si'), ('f','No')])
    color = models.CharField(max_length=100, blank=False, null=False)
    cantidad = models.PositiveIntegerField(default=0, blank=False)
    tamanio = EnumField(choices=[('c','Chico'), ('m','Mediano'), ('g','Grande')])
    alto = models.DecimalField(max_digits=10, decimal_places=3, default=0, blank=False)
    ancho = models.DecimalField(max_digits=10, decimal_places=3, default=0, blank=False)
    largo = models.DecimalField(max_digits=10, decimal_places=3, default=0, blank=False)
    ProductoCampo = models.ForeignKey('ProductoCampo',on_delete=models.CASCADE, unique=False, null=False, blank=False)

class Prueba(models.Model):
    IDPrueba = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    kilogramos = models.DecimalField(max_digits=10, decimal_places=3, default=0, blank=False)
    Caja = models.ForeignKey('Caja',on_delete=models.CASCADE,unique=False, null=False, blank=False)


class Detalle(models.Model):
    ID = models.AutoField(primary_key=True, null=False)
    cantidad_cajas = models.PositiveIntegerField(default=0, blank=False)
    Producto = models.ForeignKey('Producto',on_delete=models.CASCADE,unique=False, null=False, blank=False)
    OrdenCompra = models.ForeignKey('OrdenCompra',on_delete=models.CASCADE,unique=False, null=False, blank=False)


class OrdenCompra(models.Model):
    ID = models.AutoField(primary_key=True, null=False)
    fecha = models.DateTimeField('dia_creado', auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=3, default=0, blank=False)
    tipo_cambio = models.DecimalField(max_digits=10, decimal_places=3, default=0, blank=False)
    pagado = models.BooleanField(default=False, null=False)
    Cliente = models.ForeignKey('Cliente',on_delete=models.CASCADE,unique=False, null=False, blank=False)


class Cliente(models.Model):
    IDCliente = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    nombre = models.CharField(max_length=100, blank=True)
    apellido_paterno = models.CharField(max_length=100, blank=True)
    apellido_materno = models.CharField(max_length=100, blank=True)
    direccion = models.CharField(max_length=100, blank=True)
    localidad = models.CharField(max_length=100, blank=True)
    municipio = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=100, blank=True)
    rfc = models.CharField(max_length=13, null=False)
    telefono = models.CharField(max_length=30, blank=True)
    fecha_inclusion = models.DateTimeField('dia_creado', auto_now_add=True)

    def __str__(self):
        return self.nombre
