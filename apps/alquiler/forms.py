from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Contrato, Extra, Cliente, Reserva, Factura, Nota, Entrega
from apps.flota.models import Vehiculo
import re
from decimal import Decimal

# ----------------- FORMULARIO CLIENTE -----------------
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
            'tipo_cliente': forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo_cliente'}),
            'razon_social': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Razón Social de la empresa'}),
            'nombre_comercial': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de fantasía (opcional)'}),
            'rut_empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '76.123.456-7'}),
            'giro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Actividad comercial principal'}),
            'nombre_contacto': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos_contacto': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo_contacto': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56999999999'}),
            'telefono_contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56999999999'}),
            'email_empresa': forms.EmailInput(attrs={'class': 'form-control'}),
            'email_contacto': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'comuna': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234567'}),
            'sitio_web': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Campos opcionales para ambos tipos
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

# ----------------- FORMULARIO RESERVA -----------------
class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['cliente', 'vehiculo', 'fecha_inicio', 'fecha_fin', 'estado', 'observaciones']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'vehiculo': forms.Select(attrs={'class': 'form-select', 'id': 'id_vehiculo'}),
            'fecha_inicio': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'fecha_fin': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

# ----------------- FORMULARIO ENTREGA -----------------
class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ['is_delivery', 'direccion_entrega', 'direccion_devolucion', 'chofer', 'delivery_cost']
        widgets = {
            'is_delivery': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'direccion_entrega': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_devolucion': forms.TextInput(attrs={'class': 'form-control'}),
            'chofer': forms.TextInput(attrs={'class': 'form-control'}),
            'delivery_cost': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# ----------------- FORMULARIO CONTRATO -----------------
class ContratoForm(forms.ModelForm):
    garantia = forms.DecimalField(
        label="Garantía",
        max_digits=10,
        decimal_places=2,
        min_value=0,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    tarifa_diaria = forms.DecimalField(
        label="Tarifa diaria",
        max_digits=10,
        decimal_places=2,
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    descuento_porcentaje = forms.DecimalField(
        label="Descuento (%)",
        max_digits=5,
        decimal_places=2,
        min_value=0,
        max_value=100,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    # extras = forms.ModelMultipleChoiceField(
    #     queryset=Extra.objects.filter(activo=True),
    #     required=False,
    #     widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input', 'data-precio': ''}),
    #     label="Extras contratados"
    # )
    fecha_inicio = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        label="Fecha inicio arriendo"
    )
    fecha_fin = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        label="Fecha fin arriendo"
    )

    class Meta:
        model = Contrato
        fields = [
            'reserva',
            'cliente',
            'vehiculo',
            'fecha_inicio',
            'fecha_fin',
            'tarifa_diaria',
            'descuento_porcentaje',
            'garantia',
            'terminos_condiciones',
            'documento_pdf',
            # 'extras'  # Eliminado del formulario
        ]
        widgets = {
            'reserva': forms.Select(attrs={'class': 'form-select'}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'vehiculo': forms.Select(attrs={'class': 'form-select', 'id': 'id_vehiculo'}),
            'terminos_condiciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'documento_pdf': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['documento_pdf'].required = False
        self.fields['reserva'].required = False
        # ¡NO pongas required=False en cliente ni vehiculo!
        # Deja cliente y vehiculo como requeridos por defecto

        # Prellenar tarifa diaria según el vehículo o reserva si corresponde
        if self.instance and self.instance.pk:
            if self.instance.tarifa_diaria:
                self.fields['tarifa_diaria'].initial = self.instance.tarifa_diaria
            elif self.instance.vehiculo and hasattr(self.instance.vehiculo, 'tarifa_diaria'):
                self.fields['tarifa_diaria'].initial = self.instance.vehiculo.tarifa_diaria
        elif 'initial' in kwargs and kwargs['initial'].get('tarifa_diaria'):
            self.fields['tarifa_diaria'].initial = kwargs['initial']['tarifa_diaria']

        # Entrega embebida
        self.entrega_form = None
        if self.instance.pk and hasattr(self.instance, 'entrega'):
            self.entrega_form = EntregaForm(instance=self.instance.entrega, prefix='entrega')
        else:
            self.entrega_form = EntregaForm(prefix='entrega')

        reserva = self.initial.get('reserva') or self.data.get('reserva')
        if reserva:
            self.fields['cliente'].widget = forms.HiddenInput()
            self.fields['vehiculo'].widget = forms.HiddenInput()

        if self.instance.pk and hasattr(self.instance, 'entrega'):
            if not self.instance.puede_editar_direccion_devolucion:
                self.entrega_form.fields['direccion_devolucion'].widget.attrs['readonly'] = True

    def clean(self):
        cleaned_data = super().clean()
        print("\n[DEBUG][ContratoForm.clean] cleaned_data inicial:", dict(cleaned_data))
        print("[DEBUG][ContratoForm.clean] fields:", list(self.fields.keys()))
        print("[DEBUG][ContratoForm.clean] POST:", self.data)
        print("[DEBUG][ContratoForm.clean] FILES:", self.files)

        # Si documento_pdf no viene, ponlo None explícito
        if not cleaned_data.get('documento_pdf'):
            print("[DEBUG][ContratoForm.clean] documento_pdf vacío, lo ponemos a None")
            cleaned_data['documento_pdf'] = None

        # INTENTA limpiar el modelo, pero si hay error, ¡que explote!
        from django.core.exceptions import ValidationError
        try:
            self.instance.full_clean(exclude=['numero_contrato'])
        except ValidationError as e:
            print("[DEBUG][ContratoForm.clean] ValidationError.message_dict:", e.message_dict)
            for field, errors in e.message_dict.items():
                if field in self.fields:
                    for error in errors:
                        self.add_error(field, error)
                else:
                    self.add_error(None, f"{field}: {'; '.join(errors)}")
        except Exception as exc:
            print("EXCEPCIÓN GRAVE EN full_clean CONTRATO:", exc)
            import traceback
            traceback.print_exc()
            raise
        print("[DEBUG][ContratoForm.clean] cleaned_data final:", repr(cleaned_data))
        return cleaned_data

    def is_valid(self):
        valid = super().is_valid()
        if self.entrega_form:
            valid = valid and self.entrega_form.is_valid()
        return valid

    def clean(self):
        cleaned_data = super().clean()
        print("\n[DEBUG][ContratoForm.clean] cleaned_data inicial:", dict(cleaned_data))
        print("[DEBUG][ContratoForm.clean] fields:", list(self.fields.keys()))
        print("[DEBUG][ContratoForm.clean] POST:", self.data)
        print("[DEBUG][ContratoForm.clean] FILES:", self.files)

        # Imprime los errores por campo (si hay)
        for field in self.fields:
            if field in self.errors:
                print(f"[ERROR][{field}] {self.errors[field]}")
        print("Non-field errors:", self.non_field_errors())



        # Si documento_pdf no viene, ponlo None explícito
        if not cleaned_data.get('documento_pdf'):
            print("[DEBUG][ContratoForm.clean] documento_pdf vacío, lo ponemos a None")
            cleaned_data['documento_pdf'] = None

        # ---- Tus validaciones extra pueden ir aquí ----

        import traceback
        print("[DEBUG][ContratoForm.clean] cleaned_data final:", repr(cleaned_data))
        try:
            self.instance.full_clean(exclude=['numero_contrato'])  # No revisa el numero_contrato si lo llenas en save()
        except Exception as e:
            print("==== Exception en full_clean Contrato ====")
            print(e)
            traceback.print_exc()
            self.add_error(None, f"Error en validación Contrato: {str(e)}")

        # Añadir test: si no hay errores pero el form es inválido, agregar error especial
        if not self.errors:
            self.add_error(None, "Prueba: No se detectó error, pero el form es inválido. cleaned_data: %s" % repr(cleaned_data))
        return cleaned_data
        self.calculadora_context = {
            'dias': dias,
            'subtotal_base': subtotal_base,
            'total_extras': total_extras,
            'delivery_cost': delivery_cost,
            'subtotal': subtotal,
            'descuento_aplicado': descuento_aplicado,
            'subtotal_final': subtotal_final,
            'iva': iva,
            'monto_total': monto_total,
        }
        return cleaned_data

    def save(self, commit=True):
        contrato = super().save(commit=False)

        # Generar numero_contrato solo si es nuevo
        if not contrato.pk or not contrato.numero_contrato:
            from datetime import datetime
            anio = contrato.fecha_inicio.year if contrato.fecha_inicio else datetime.now().year
            ultimo = Contrato.objects.filter(numero_contrato__startswith=f"C{anio}").order_by('-numero_contrato').first()
            if ultimo and ultimo.numero_contrato:
                try:
                    corr = int(ultimo.numero_contrato[-4:]) + 1
                except:
                    corr = 1
            else:
                corr = 1
            contrato.numero_contrato = f"C{anio}{corr:04d}"

        # Estado inicial: POR_FIRMAR
        if not contrato.pk:
            contrato.estado = 'POR_FIRMAR'
        if commit:
            try:
                contrato.full_clean()
            except Exception as e:
                print(">>> EXCEPCIÓN EN full_clean:", e)
                import traceback; traceback.print_exc()
            contrato.save()
            self.save_m2m()
        # Guardar datos de entrega
        if self.entrega_form and self.entrega_form.is_valid():
            entrega = self.entrega_form.save(commit=False)
            entrega.contrato = contrato
            entrega.save()
        return contrato

# ----------------- FORMULARIO AGREGAR EXTRA A CONTRATO -----------------
class ContratoAddExtraForm(forms.Form):
    extra = forms.ModelChoiceField(
        queryset=Extra.objects.filter(activo=True),
        label="Extra a agregar",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

# ----------------- FORMULARIO FACTURA -----------------
class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = '__all__'
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

# ----------------- FORMULARIO NOTA -----------------
class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['tipo', 'motivo', 'monto', 'observaciones']