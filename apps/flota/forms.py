from django import forms
from .models import Vehiculo, GrupoVehiculo, Marca, ModeloVehiculo, KilometrajeVehiculo

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = [
            'grupo', 'modelo', 'patente', 'vin', 'traccion', 'tenencia', 'anio_fabricacion', 'color',
            'transmision', 'combustible', 'capacidad', 'numero_asientos', 'estado_general', 'subestado',
            'kilometraje_actual', 'proximo_mantenimiento',
            'observaciones', 'fecha_vencimiento_soap', 'archivo_soap', 'fecha_vencimiento_rev_tecnica',
            'archivo_rev_tecnica', 'fecha_vencimiento_permiso_circulacion', 'archivo_permiso_circulacion',
            'fecha_vencimiento_homologacion', 'archivo_homologacion'
        ]
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 3}),
            'fecha_vencimiento_soap': forms.DateInput(attrs={'type': 'date'}),
            'fecha_vencimiento_rev_tecnica': forms.DateInput(attrs={'type': 'date'}),
            'fecha_vencimiento_permiso_circulacion': forms.DateInput(attrs={'type': 'date'}),
            'fecha_vencimiento_homologacion': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_patente(self):
        patente = self.cleaned_data.get('patente', '').upper()
        if Vehiculo.objects.exclude(pk=self.instance.pk).filter(patente=patente).exists():
            raise forms.ValidationError("Ya existe un vehículo con esta patente.")
        return patente

    def clean_vin(self):
        vin = self.cleaned_data.get('vin', '').upper()
        if Vehiculo.objects.exclude(pk=self.instance.pk).filter(vin=vin).exists():
            raise forms.ValidationError("Ya existe un vehículo con este VIN/Chasis.")
        return vin

    def clean(self):
        cleaned_data = super().clean()
        # Validación cruzada de documentos: si sube archivo, fecha obligatoria y viceversa
        doc_pairs = [
            ('archivo_soap', 'fecha_vencimiento_soap'),
            ('archivo_rev_tecnica', 'fecha_vencimiento_rev_tecnica'),
            ('archivo_permiso_circulacion', 'fecha_vencimiento_permiso_circulacion'),
            ('archivo_homologacion', 'fecha_vencimiento_homologacion'),
        ]
        for file_field, date_field in doc_pairs:
            file_val = cleaned_data.get(file_field)
            date_val = cleaned_data.get(date_field)
            if file_val and not date_val:
                self.add_error(date_field, "Debe indicar la fecha de vencimiento si sube un archivo.")
            if date_val and not file_val:
                self.add_error(file_field, "Debe adjuntar el archivo correspondiente si ingresa la fecha.")
        return cleaned_data

class GrupoVehiculoForm(forms.ModelForm):
    class Meta:
        model = GrupoVehiculo
        fields = ['nombre', 'descripcion']

class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ['nombre', 'pais_origen']

class ModeloVehiculoForm(forms.ModelForm):
    class Meta:
        model = ModeloVehiculo
        fields = ['marca', 'nombre', 'tipo_carroceria']

class KilometrajeVehiculoForm(forms.ModelForm):
    SALTO_MAXIMO_KM = 3000

    confirmar_salto = forms.BooleanField(
        required=False,
        label="¿Está de acuerdo con el salto de kilómetros?",
        help_text="Confirme si el salto de kilómetros es correcto.",
    )

    class Meta:
        model = KilometrajeVehiculo
        fields = ['vehiculo', 'kilometraje', 'tipo_evento', 'observaciones', 'confirmar_salto']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.salto_detectado = False
        self.salto_valor = None

    def clean(self):
        cleaned_data = super().clean()
        vehiculo = cleaned_data.get('vehiculo')
        kilometraje = cleaned_data.get('kilometraje')
        confirmar_salto = cleaned_data.get('confirmar_salto')
        if vehiculo and kilometraje is not None:
            ultimo_registro = vehiculo.historial_kilometraje.order_by('-fecha').first()
            if ultimo_registro:
                if kilometraje < ultimo_registro.kilometraje:
                    self.add_error('kilometraje', 'El kilometraje no puede ser menor al último registrado.')
                salto = kilometraje - ultimo_registro.kilometraje
                if salto > self.SALTO_MAXIMO_KM:
                    self.salto_detectado = True
                    self.salto_valor = salto
                    if not confirmar_salto:
                        # Solo muestra el error si no está confirmado
                        self.add_error(
                            'confirmar_salto',
                            f"¡Advertencia! El salto de kilómetros es muy grande ({salto:,} km). ¿Está de acuerdo?"
                        )
        return cleaned_data