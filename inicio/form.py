from django import forms
from enumfields import EnumField
from enumfields import Enum  # Uses Ethan Furman's "enum34" backport
from django.forms import ModelForm
from inicio.models import ProductoCampo, Caja, Prueba

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class' : 'validate','id' : 'validate'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class' : 'validate','id' : 'validate'}))

class NuevaRecepcion(ModelForm):
    class Meta:
        model = ProductoCampo
        fields = ['calidad_aprox', 'status', 'representante','Productor','firma']

class NuevaCaja(ModelForm):
    class Meta:
        model = Caja
        fields = ['peso_neto','color','cantidad','tamanio','alto','ancho','largo']

class NuevaPrueba(ModelForm):
    class Meta:
        model = Prueba
        fields = ['kilogramos']
