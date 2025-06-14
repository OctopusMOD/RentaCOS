from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Cliente, Reserva, Contrato, Factura, Nota  # Vehiculo removido temporalmente
import re
from decimal import Decimal

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'tipo_cliente',
            # Datos empresa
            'razon_social', 'nombre_comercial', 'rut_empresa', 'giro',
            # Datos contacto
            'nombre_contacto', 'apellidos_contacto', 'cargo_contacto',
            'tipo_documento', 'numero_documento',
            # Contacto
            'telefono_empresa', 'telefono_contacto',
            'email_empresa', 'email_contacto',
            # Dirección
            'direccion', 'comuna', 'ciudad', 'region', 'codigo_postal',
            # Adicionales
            'sitio_web', 'observaciones'
        ]
        widgets = {
            'tipo_cliente': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_tipo_cliente'
            }),
            'razon_social': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Razón Social de la empresa'
            }),
            'nombre_comercial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de fantasía (opcional)'
            }),
            'rut_empresa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '76.123.456-7'
            }),
            'giro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Actividad comercial principal'
            }),
            'nombre_contacto': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'apellidos_contacto': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'cargo_contacto': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'tipo_documento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'telefono_empresa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56999999999'
            }),
            'telefono_contacto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56999999999'
            }),
            'email_empresa': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'email_contacto': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'comuna': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'region': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'codigo_postal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1234567'
            }),
            'sitio_web': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Todos los campos opcionales o condicionales deben ser no requeridos aquí;
        # la validación obligatoria se maneja en clean según tipo_cliente
        self.fields['nombre_comercial'].required = False
        self.fields['sitio_web'].required = False
        self.fields['codigo_postal'].required = False
        self.fields['observaciones'].required = False
        self.fields['razon_social'].required = False
        self.fields['rut_empresa'].required = False
        self.fields['giro'].required = False
        self.fields['email_empresa'].required = False
        self.fields['telefono_empresa'].required = False
        self.fields['cargo_contacto'].required = False
        self.fields['nombre_contacto'].required = False
        self.fields['apellidos_contacto'].required = False
        self.fields['tipo_documento'].required = False
        self.fields['numero_documento'].required = False
        self.fields['telefono_contacto'].required = False
        self.fields['email_contacto'].required = False

    def clean(self):
        cleaned_data = super().clean()
        tipo_cliente = cleaned_data.get('tipo_cliente')

        if tipo_cliente == 'EMPRESA':
            required_fields = {
                'razon_social': 'La razón social es obligatoria para empresas',
                'rut_empresa': 'El RUT es obligatorio para empresas',
                'giro': 'El giro comercial es obligatorio para empresas',
                'email_empresa': 'El email de la empresa es obligatorio',
                'telefono_empresa': 'El teléfono de la empresa es obligatorio'
            }
            for field, message in required_fields.items():
                if not cleaned_data.get(field):
                    self.add_error(field, message)
            # NO se valida aquí el formato del RUT, solo requeridos

            telefono = cleaned_data.get('telefono_empresa')
            if telefono and not re.match(r'^\+?56?\d{9}$', telefono):
                self.add_error('telefono_empresa', 'El número debe estar en formato: +56999999999')
            # Limpiar campos de persona
            cleaned_data['telefono_contacto'] = None
            cleaned_data['email_contacto'] = None
            cleaned_data['nombre_contacto'] = None
            cleaned_data['apellidos_contacto'] = None
            cleaned_data['tipo_documento'] = None
            cleaned_data['numero_documento'] = None

        elif tipo_cliente == 'PERSONA':
            required_fields = {
                'nombre_contacto': 'El nombre es obligatorio',
                'apellidos_contacto': 'Los apellidos son obligatorios',
                'tipo_documento': 'El tipo de documento es obligatorio',
                'numero_documento': 'El número de documento es obligatorio',
                'email_contacto': 'El email de contacto es obligatorio',
                'telefono_contacto': 'El teléfono de contacto es obligatorio'
            }
            for field, message in required_fields.items():
                if not cleaned_data.get(field):
                    self.add_error(field, message)
            telefono = cleaned_data.get('telefono_contacto')
            if telefono and not re.match(r'^\+?56?\d{9}$', telefono):
                self.add_error('telefono_contacto', 'El número debe estar en formato: +56999999999')
            # Limpiar campos de empresa
            cleaned_data['telefono_empresa'] = None
            cleaned_data['email_empresa'] = None
            cleaned_data['razon_social'] = None
            cleaned_data['rut_empresa'] = None
            cleaned_data['giro'] = None
            cleaned_data['cargo_contacto'] = None

        return cleaned_data

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['cliente', 'fecha_inicio', 'fecha_fin', 'estado', 'observaciones']  # vehiculo removido
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'fecha_fin': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            )
        }

class ContratoForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(),
        required=False,
        label='Cliente',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    class Meta:
        model = Contrato
        fields = ['reserva', 'cliente', 'terminos_condiciones', 'documento_pdf']  # vehiculo removido
        widgets = {
            'reserva': forms.Select(attrs={'class': 'form-select'}),
            'terminos_condiciones': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 5}
            ),
            'documento_pdf': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reserva'].required = False
        # Filtrar solo reservas sin contrato y que no estén canceladas
        self.fields['reserva'].queryset = Reserva.objects.filter(
            contrato__isnull=True
        ).exclude(estado='CANCELADA')
        # Oculta cliente si hay reserva seleccionada
        if self.initial.get('reserva') or self.data.get('reserva'):
            self.fields['cliente'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        reserva = cleaned_data.get('reserva')
        cliente = cleaned_data.get('cliente')
        # Si NO hay reserva, cliente es obligatorio
        if not reserva:
            if not cliente:
                self.add_error('cliente', 'Debes seleccionar un cliente.')
        return cleaned_data

class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = '__all__'  # Incluye todos los campos del modelo Factura
        widgets = {
            'numero_factura': forms.TextInput(attrs={'class': 'form-control'}),
            'contrato': forms.Select(attrs={'class': 'form-select'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'fecha_emision': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'iva': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': True}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': True}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'rut_emisor': forms.TextInput(attrs={'class': 'form-control'}),
            'rut_receptor': forms.TextInput(attrs={'class': 'form-control'}),
            'razon_social_receptor': forms.TextInput(attrs={'class': 'form-control'}),
            'giro_receptor': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_receptor': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        subtotal = cleaned_data.get('subtotal')
        if subtotal is not None:
            iva = round(subtotal * Decimal('0.19'), 2)
            total = round(subtotal + iva, 2)
            cleaned_data['iva'] = iva
            cleaned_data['total'] = total
            self.instance.iva = iva
            self.instance.total = total
        return cleaned_data

class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['tipo', 'motivo', 'monto', 'observaciones']