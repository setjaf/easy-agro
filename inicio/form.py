from django import forms
from enumfields import EnumField
from enumfields import Enum  # Uses Ethan Furman's "enum34" backport
from django.forms import ModelForm
from inicio.models import ProductoCampo, Caja, Prueba, Productor, ProductoCorrida, Empleado, Usuario, Status_pc, Status_pco
from betterforms.multiform import MultiModelForm

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class' : 'validate','id' : 'validate'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class' : 'validate','id' : 'validate'}))

class filtroProductor(forms.Form):
    localidad = forms.ChoiceField(widget=forms.Select(attrs={'id' : 'loc'}), initial='Your name')
    municipio = forms.ChoiceField(widget=forms.Select(attrs={'id' : 'mun'}), initial='Your name')

class Recepcion(ModelForm):
    class Meta:
        model = ProductoCampo
        fields = ['calidad_aprox', 'representante','Productor','firma']

class Status_rec(ModelForm):
    class Meta:
        model = Status_pc
        fields = ['estado']

class NuevaRecepcion(MultiModelForm):
    form_classes = {
        'recepcion':Recepcion,
        'status':Status_rec,
    }

class NuevaCaja(ModelForm):
    class Meta:
        model = Caja
        fields = ['peso_neto','color','cantidad','tamanio','alto','ancho','largo']

class NuevaPrueba(ModelForm):
    class Meta:
        model = Prueba
        fields = ['kilogramos']
class Corrida(ModelForm):
    class Meta:
        model = ProductoCorrida
        fields=['calibre','kilogramos','folio','Producto','ProductoCampo']
        widget = {
            'fecha_compra': forms.CharField(required=False,widget=forms.TextInput(attrs={'class':'datepicker'})),
            'calibre': forms.ChoiceField(widget=forms.Select())
        }

class Status_cor(ModelForm):
    class Meta:
        model = Status_pco
        fields = ['estado']

class NuevaCorrida(MultiModelForm):
    form_classes = {
        'corrida':Corrida,
        'status':Status_cor,
    }

class NuevoEmpleado(ModelForm):
    class Meta:
        model = Empleado
        exclude = ['IDEmpleado']

class NuevoUsuario(ModelForm):
    class Meta:
        model = Usuario
        fields = ['email','password','avatar']
        widget = {
            'password': forms.PasswordInput(attrs={'class':'pass'})
        }

class MultiEmUs(MultiModelForm):
    form_classes = {
        'usuario':NuevoUsuario,
        'empleado':NuevoEmpleado,
    }

class Multiforms(MultiModelForm):
    form_classes = {
        'caja':NuevaCaja,
        'prueba1':NuevaPrueba,
        'prueba2':NuevaPrueba,
        'prueba3':NuevaPrueba,
    }

class CajaNueva1(MultiModelForm):
    form_classes = {
        'caja':NuevaCaja,
        'prueba1':NuevaPrueba,
        'prueba2':NuevaPrueba,
        'prueba3':NuevaPrueba,
    }

class CajaNueva2(MultiModelForm):
    form_classes = {
        'caja':NuevaCaja,
        'prueba1':NuevaPrueba,
        'prueba2':NuevaPrueba,
        'prueba3':NuevaPrueba,
    }

class CajaNueva3(MultiModelForm):
    form_classes = {
        'caja':NuevaCaja,
        'prueba1':NuevaPrueba,
        'prueba2':NuevaPrueba,
        'prueba3':NuevaPrueba,
    }
