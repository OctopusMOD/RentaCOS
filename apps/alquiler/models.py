from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import re

TIPOS_DOC = [
    ('33', 'Factura Electrónica'),
    ('34', 'Factura Exenta Electrónica'),
    ('39', 'Boleta Electrónica'),
    ('41', 'Boleta Exenta Electrónica'),
    # Puedes agregar más según SII
]

ESTADOS_FACTURA = [
    ('EMITIDA', 'Emitida'),
    ('PAGADA', 'Pagada'),
    ('ANULADA', 'Anulada'),
]

class Cliente(models.Model):
    """Modelo para almacenar la información de los clientes empresariales en Chile."""

    TIPO_CLIENTE_CHOICES = [
        ('EMPRESA', 'Empresa'),
        ('PERSONA', 'Persona Natural'),
    ]

    TIPO_DOCUMENTO_CHOICES = [
        ('RUT', 'RUT'),
        ('PASAPORTE', 'Pasaporte'),
        ('DNI', 'DNI'),
        ('OTRO', 'Otro'),
    ]

    tipo_cliente = models.CharField(
        max_length=20,
        choices=TIPO_CLIENTE_CHOICES,
        default='EMPRESA',
        verbose_name="Tipo de Cliente"
    )
    razon_social = models.CharField(
        max_length=200,
        verbose_name="Razón Social",
        help_text="Nombre legal de la empresa",
        default="",
        blank=True, null=True
    )
    nombre_comercial = models.CharField(
        max_length=200,
        verbose_name="Nombre Comercial",
        blank=True,
        help_text="Nombre comercial o de fantasía",
        default=""
    )
    rut_empresa = models.CharField(
        max_length=12,
        verbose_name="RUT Empresa",
        help_text="Formato: XX.XXX.XXX-X",
        default="",
        blank=True, null=True
    )
    giro = models.CharField(
        max_length=200,
        verbose_name="Giro Comercial",
        help_text="Actividad comercial principal",
        default="",
        blank=True, null=True
    )
    nombre_contacto = models.CharField(
        max_length=100,
        verbose_name="Nombre Contacto",
        default="",
        blank=True, null=True
    )
    apellidos_contacto = models.CharField(
        max_length=100,
        verbose_name="Apellidos Contacto",
        default="",
        blank=True, null=True
    )
    cargo_contacto = models.CharField(
        max_length=100,
        verbose_name="Cargo del Contacto",
        default="",
        blank=True, null=True
    )
    tipo_documento = models.CharField(
        max_length=20,
        choices=TIPO_DOCUMENTO_CHOICES,
        default='RUT',
        verbose_name="Tipo de Documento",
        blank=True, null=True
    )
    numero_documento = models.CharField(
        max_length=20,
        verbose_name="Número de Documento",
        default="",
        blank=True, null=True
    )
    telefono_empresa = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?56?\d{9}$',
                message="El número debe estar en formato: '+56999999999'"
            )
        ],
        verbose_name="Teléfono Empresa",
        default="+56",
        blank=True, null=True
    )
    telefono_contacto = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?56?\d{9}$',
                message="El número debe estar en formato: '+56999999999'"
            )
        ],
        verbose_name="Teléfono Contacto",
        default="+56",
        blank=True, null=True
    )
    email_empresa = models.EmailField(
        verbose_name="Email Empresa",
        default="",
        blank=True, null=True
    )
    email_contacto = models.EmailField(
        verbose_name="Email Contacto",
        default="",
        blank=True, null=True
    )
    direccion = models.CharField(
        max_length=255,
        verbose_name="Dirección",
        default="",
        blank=True
    )
    comuna = models.CharField(
        max_length=100,
        verbose_name="Comuna",
        default="",
        blank=True
    )
    ciudad = models.CharField(
        max_length=100,
        verbose_name="Ciudad",
        default="",
        blank=True
    )
    region = models.CharField(
        max_length=100,
        verbose_name="Región",
        default="",
        blank=True
    )
    codigo_postal = models.CharField(
        max_length=7,
        verbose_name="Código Postal",
        blank=True,
        default=""
    )
    sitio_web = models.URLField(
        blank=True,
        verbose_name="Sitio Web",
        default=""
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones",
        default=""
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Registro"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Cliente Activo"
    )

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['-fecha_registro']
        unique_together = [['tipo_cliente', 'rut_empresa']]

    def __str__(self):
        if self.tipo_cliente == 'EMPRESA':
            return f"{self.razon_social} (RUT: {self.rut_empresa})"
        return f"{self.nombre_contacto} {self.apellidos_contacto}"

    def clean(self):
        if self.tipo_cliente == 'EMPRESA':
            if not self.razon_social:
                raise ValidationError({'razon_social': 'La razón social es obligatoria para empresas.'})
            rut = self.rut_empresa.strip() if self.rut_empresa else ''
            print(f"[DEBUG] Validando RUT: '{rut}' para Cliente (ID: {self.id})")
            if not rut:
                raise ValidationError({'rut_empresa': 'El RUT es obligatorio para empresas.'})
            if rut and not re.match(r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$', rut):
                raise ValidationError({'rut_empresa': 'El RUT debe tener el formato XX.XXX.XXX-X'})
            if Cliente.objects.filter(
                tipo_cliente='EMPRESA',
                rut_empresa=self.rut_empresa
            ).exclude(id=self.id).exists():
                raise ValidationError({'rut_empresa': 'Este RUT ya está registrado.'})

    def save(self, *args, **kwargs):
        self.clean()
        if self.nombre_comercial:
            self.nombre_comercial = self.nombre_comercial.title()
        if self.nombre_contacto:
            self.nombre_contacto = self.nombre_contacto.title()
        if self.apellidos_contacto:
            self.apellidos_contacto = self.apellidos_contacto.title()
        if self.comuna:
            self.comuna = self.comuna.title()
        if self.ciudad:
            self.ciudad = self.ciudad.title()
        super().save(*args, **kwargs)

class Reserva(models.Model):
    """Modelo para gestionar las reservas de vehículos."""

    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]

    cliente = models.ForeignKey(
        'Cliente',
        on_delete=models.PROTECT,
        related_name='reservas',
        verbose_name="Cliente"
    )
    # vehiculo = models.ForeignKey(
    #     'flota.Vehiculo',
    #     on_delete=models.PROTECT,
    #     related_name='reservas',
    #     verbose_name="Vehículo"
    # )
    # Vehiculo removido temporalmente
    fecha_inicio = models.DateTimeField(
        verbose_name="Fecha de Inicio"
    )
    fecha_fin = models.DateTimeField(
        verbose_name="Fecha de Fin"
    )
    fecha_reserva = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Reserva"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE',
        verbose_name="Estado"
    )
    monto_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Monto Total"
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )

    # Métodos de permisos
    def puede_editar(self):
        return self.estado == "PENDIENTE"

    def puede_eliminar(self):
        return self.estado == "PENDIENTE"

    def puede_confirmar(self):
        return self.estado == "PENDIENTE"

    def puede_cancelar(self):
        return self.estado in ["PENDIENTE", "CONFIRMADA"]

    def puede_asociar_contrato(self):
        return self.estado == "CONFIRMADA"

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-fecha_reserva']

    def __str__(self):
        return f"Reserva #{self.id} - {self.cliente} - {self.estado}"

    def clean(self):
        super().clean()
        now = timezone.now()
        # Permite guardar reservas existentes aunque la fecha_inicio esté en el pasado, solo exige futuro en creación o PENDIENTE
        if (not self.pk or self.estado == "PENDIENTE") and self.fecha_inicio < now:
            raise ValidationError({'fecha_inicio': 'La fecha de inicio debe ser posterior a la fecha actual.'})
        if self.fecha_inicio and self.fecha_fin:
            if self.fecha_inicio < timezone.now():
                raise ValidationError({'fecha_inicio': 'La fecha de inicio debe ser posterior a la fecha actual.'})
            if self.fecha_fin <= self.fecha_inicio:
                raise ValidationError({'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'})
            # reservas_conflictivas = Reserva.objects.filter(
            #     vehiculo=self.vehiculo,
            #     estado__in=['PENDIENTE', 'CONFIRMADA', 'EN_PROGRESO'],
            #     fecha_inicio__lt=self.fecha_fin,
            #     fecha_fin__gt=self.fecha_inicio
            # ).exclude(id=self.id)
            # if reservas_conflictivas.exists():
            #     raise ValidationError('El vehículo no está disponible en las fechas seleccionadas.')
            # Vehiculo removido temporalmente

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Contrato(models.Model):
    """Modelo para gestionar los contratos de alquiler."""

    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('FIRMADO', 'Firmado'),
        ('ACTIVO', 'Activo'),
        ('FINALIZADO', 'Finalizado'),
        ('CANCELADO', 'Cancelado'),
    ]

    # Cambiado: reserva es opcional, on_delete SET_NULL
    reserva = models.OneToOneField(
        'Reserva',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contrato',
        verbose_name="Reserva"
    )
    numero_contrato = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de Contrato"
    )
    fecha_firma = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Firma"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='BORRADOR',
        verbose_name="Estado"
    )
    terminos_condiciones = models.TextField(
        verbose_name="Términos y Condiciones"
    )
    documento_pdf = models.FileField(
        upload_to='contratos/',
        null=True,
        blank=True,
        verbose_name="Documento PDF"
    )

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        ordering = ['-fecha_firma']

    def __str__(self):
        if self.reserva:
            return f"Contrato {self.numero_contrato} - {self.reserva.cliente}"
        return f"Contrato {self.numero_contrato} - Sin Reserva"

class Factura(models.Model):
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name='facturas')
    tipo_documento = models.CharField(max_length=4, choices=TIPOS_DOC, default='33')
    numero_factura = models.CharField(max_length=20, unique=True)
    fecha_emision = models.DateTimeField(default=timezone.now)
    fecha_vencimiento = models.DateField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    iva = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=10, choices=ESTADOS_FACTURA, default='EMITIDA')
    sii_track_id = models.CharField(max_length=40, blank=True, null=True, help_text='ID de seguimiento SII (si aplica)')
    sii_xml = models.TextField(blank=True, null=True, help_text='XML enviado/recibido del SII (opcional)')
    rut_emisor = models.CharField(max_length=12, help_text='RUT empresa que emite')
    rut_receptor = models.CharField(max_length=12, help_text='RUT cliente')
    razon_social_receptor = models.CharField(max_length=100)
    giro_receptor = models.CharField(max_length=100)
    direccion_receptor = models.CharField(max_length=150)

    def __str__(self):
        return f"Factura {self.numero_factura} ({self.get_tipo_documento_display()}) - {self.contrato}"

    class Meta:
        ordering = ['-fecha_emision']

class Nota(models.Model):
    TIPO_NOTA_CHOICES = [
        ('CREDITO', 'Nota de Crédito'),
        ('DEBITO', 'Nota de Débito'),
    ]
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='notas')
    tipo = models.CharField(max_length=10, choices=TIPO_NOTA_CHOICES)
    fecha_emision = models.DateTimeField(default=timezone.now)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    motivo = models.TextField(blank=True)
    observaciones = models.TextField(blank=True, null=True)
    numero = models.CharField(max_length=30, unique=True, help_text='Número interno o folio SII si ya integrado')
    sii_track_id = models.CharField(max_length=40, blank=True, null=True, help_text='ID de seguimiento SII (si aplica)')
    sii_xml = models.TextField(blank=True, null=True, help_text='XML enviado/recibido del SII (opcional)')

    class Meta:
        ordering = ['-fecha_emision']
        verbose_name = 'Nota de Crédito/Débito'
        verbose_name_plural = 'Notas de Crédito/Débito'

    def __str__(self):
        return f"{self.get_tipo_display()} {self.numero} para Factura {self.factura.numero_factura}"