from django import forms
from django.forms import inlineformset_factory
from .models import TipoMantenimiento, OrdenMantenimiento, ItemRepuesto, ConsumoRepuesto, Taller, TrabajoRealizado

class TipoMantenimientoForm(forms.ModelForm):
    class Meta:
        model = TipoMantenimiento
        fields = ['nombre', 'es_preventivo']

class TallerForm(forms.ModelForm):
    class Meta:
        model = Taller
        fields = ['nombre', 'direccion', 'telefono', 'contacto']

class OrdenMantenimientoForm(forms.ModelForm):
    class Meta:
        model = OrdenMantenimiento
        fields = [
            'vehiculo', 'taller', 'tipo', 'estado',
            'fecha_ingreso', 'fecha_salida',
            'descripcion_problema', 'diagnostico', 'tecnico_responsable', 'observaciones'
        ]
        widgets = {
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}),
            'fecha_salida': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        estado = cleaned_data.get('estado')
        fecha_ingreso = cleaned_data.get('fecha_ingreso')
        fecha_salida = cleaned_data.get('fecha_salida')

        if estado in ['PENDIENTE', 'EN_PROCESO', 'COMPLETADO'] and not fecha_ingreso:
            self.add_error('fecha_ingreso', "Debe ingresar la fecha de entrada al taller.")
        if estado == 'COMPLETADO':
            if not fecha_salida:
                self.add_error('fecha_salida', "Debe ingresar la fecha de salida del taller.")
            if fecha_ingreso and fecha_salida and fecha_salida < fecha_ingreso:
                self.add_error('fecha_salida', "La fecha de salida no puede ser anterior a la de entrada.")
        return cleaned_data

class ItemRepuestoForm(forms.ModelForm):
    class Meta:
        model = ItemRepuesto
        fields = ['nombre', 'codigo', 'cantidad_stock', 'descripcion']

class ConsumoRepuestoForm(forms.ModelForm):
    class Meta:
        model = ConsumoRepuesto
        fields = ['orden', 'repuesto', 'cantidad', 'observaciones']

class TrabajoRealizadoForm(forms.ModelForm):
    class Meta:
        model = TrabajoRealizado
        fields = ['codigo', 'descripcion', 'unidades', 'valor_unitario']

TrabajoRealizadoFormSet = inlineformset_factory(
    OrdenMantenimiento, TrabajoRealizado, form=TrabajoRealizadoForm, extra=1, can_delete=True
)

ConsumoRepuestoFormSet = inlineformset_factory(
    OrdenMantenimiento, ConsumoRepuesto, form=ConsumoRepuestoForm, extra=1, can_delete=True
)