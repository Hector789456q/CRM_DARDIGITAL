from django import forms
from .models import Venta

class VentaAsesorForm(forms.ModelForm):
    """Formulario para que el asesor registre una venta"""
    
    class Meta:
        model = Venta
        fields = [
            'modalidad',
            'turno',
            'cliente_nombre',
            'cliente_dni',
            'cliente_telefono',
            'cliente_direccion',
            'cliente_genero',
            'producto_servicio',
            'monto',
            'observaciones',
        ]
        widgets = {
            'modalidad': forms.Select(attrs={'class': 'form-control'}),
            'turno': forms.Select(attrs={'class': 'form-control'}),
            'cliente_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'cliente_dni': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12345678', 'maxlength': '8'}),
            'cliente_telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '987654321'}),
            'cliente_direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cliente_genero': forms.Select(attrs={'class': 'form-control'}),
            'producto_servicio': forms.TextInput(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones adicionales...'}),
        }


class VentaBackOfficeForm(forms.ModelForm):
    """Formulario para que Back Office complete los datos"""
    
    class Meta:
        model = Venta
        fields = [
            'sec',
            'sot',
            'fecha_instalacion_programada',
        ]
        widgets = {
            'sec': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SEC'}),
            'sot': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SOT'}),
            'fecha_instalacion_programada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }