from django import forms
from django.forms import inlineformset_factory
from .models import (
    TipoMantenimiento, OrdenMantenimiento, Taller, TrabajoRealizado,
    OrdenIngreso, TrabajoSolicitado, RepuestoUtilizado, EstadoMantenimiento
)

class TipoMantenimientoForm(forms.ModelForm):
    class Meta:
        model = TipoMantenimiento
        fields = ['nombre', 'es_preventivo']


# --- Formulario para Taller extendido ---
class TallerForm(forms.ModelForm):
    class Meta:
        model = Taller
        fields = [
            'razon_social', 'nombre', 'rut', 'giro_comercial',
            'direccion', 'comuna', 'region', 'telefono', 'email',
            'representante_legal', 'rut_representante',
            'tipos_servicio', 'dias_horarios', 'sitio_web', 'redes_sociales', 'logo', 'ubicacion_mapa',
            'estado'
        ]
        widgets = {
            'razon_social': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'rut': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'giro_comercial': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'comuna': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'region': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'representante_legal': forms.TextInput(attrs={'class': 'form-control'}),
            'rut_representante': forms.TextInput(attrs={'class': 'form-control'}),
            'tipos_servicio': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Ej: mecánica general, electricidad, frenos'}),
            'dias_horarios': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Ej: Lunes a Viernes 9:00 a 18:00'}),
            'sitio_web': forms.URLInput(attrs={'class': 'form-control'}),
            'redes_sociales': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: https://facebook.com/mi-taller'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'ubicacion_mapa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Embed o link de Google Maps'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

class OrdenMantenimientoForm(forms.ModelForm):
    class Meta:
        model = OrdenMantenimiento
        fields = [
            'vehiculo', 'kilometraje_ingreso_mantenimiento', 'taller', 'tipo',
            'estado', 'fecha_ingreso', 'fecha_salida', 'descripcion_problema'
        ]
        widgets = {
            'fecha_ingreso': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'fecha_salida': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'descripcion_problema': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'taller': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'vehiculo': 'Patente',
            'kilometraje_ingreso_mantenimiento': 'Kilometraje ingreso mantenimiento',
            'taller': 'Taller',
            'tipo': 'Tipo de mantenimiento',
            'estado': 'Estado',
            'fecha_ingreso': 'Fecha y hora de ingreso',
            'fecha_salida': 'Fecha y hora de salida',
            'descripcion_problema': 'Observaciones del ingreso',
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_ingreso = cleaned_data.get('fecha_ingreso')
        fecha_salida = cleaned_data.get('fecha_salida')
        if fecha_salida and fecha_ingreso and fecha_salida < fecha_ingreso:
            self.add_error('fecha_salida', "La fecha de salida no puede ser anterior a la de ingreso.")
        return cleaned_data

class TrabajoRealizadoForm(forms.ModelForm):
    class Meta:
        model = TrabajoRealizado
        fields = ['codigo', 'descripcion', 'componente', 'valor', 'unidades']
        widgets = {
            'componente': forms.Select(attrs={'class': 'form-select'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control'}),
            'unidades': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class RepuestoUtilizadoForm(forms.ModelForm):
    class Meta:
        model = RepuestoUtilizado
        fields = ['codigo', 'descripcion', 'valor', 'unidades']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control'}),
            'unidades': forms.NumberInput(attrs={'class': 'form-control'}),
        }


from django.core.exceptions import ValidationError

class OrdenIngresoForm(forms.ModelForm):
    class Meta:
        model = OrdenIngreso
        fields = ['vehiculo', 'fecha_ingreso', 'tipo_mantenimiento', 'taller', 'kilometraje_actual']
        widgets = {
            'fecha_ingreso': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'vehiculo': forms.Select(attrs={'class': 'form-select'}),
            'tipo_mantenimiento': forms.Select(attrs={'class': 'form-select'}),
            'taller': forms.Select(attrs={'class': 'form-select'}),
            'kilometraje_actual': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        vehiculo = cleaned_data.get('vehiculo')
        if vehiculo:
            # Evitar dos órdenes de ingreso abiertas para el mismo vehículo
            existe = OrdenIngreso.objects.filter(vehiculo=vehiculo).exclude(pk=self.instance.pk).exists()
            if existe:
                raise ValidationError("Ya existe una orden de ingreso abierta para este vehículo.")
        return cleaned_data

TrabajoRealizadoFormSet = inlineformset_factory(
    OrdenMantenimiento, TrabajoRealizado, form=TrabajoRealizadoForm,
    extra=1, can_delete=True
)

RepuestoUtilizadoFormSet = inlineformset_factory(
    OrdenMantenimiento, RepuestoUtilizado, form=RepuestoUtilizadoForm, extra=1, can_delete=True
)

TrabajoSolicitadoFormSet = inlineformset_factory(
    OrdenIngreso,
    TrabajoSolicitado,
    fields=['descripcion'],
    extra=1,
    can_delete=True
)