from django.db import models
from apps.flota.models import Vehiculo
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import re

# ---- ContratoPeriodo ----
class ContratoPeriodo(models.Model):
    """Periodo de arriendo de un vehículo dentro de un contrato (para extensiones, reemplazos, etc)."""
    contrato = models.ForeignKey("Contrato", related_name="periodos", on_delete=models.CASCADE)
    vehiculo = models.ForeignKey("flota.Vehiculo", on_delete=models.PROTECT)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()

    class Meta:
        ordering = ["fecha_inicio"]
        verbose_name = "Período de Contrato"
        verbose_name_plural = "Períodos de Contrato"


    def clean(self):
        # Validar fechas
        if self.fecha_fin <= self.fecha_inicio:
            raise ValidationError("La fecha de fin debe ser posterior a la de inicio.")

        # Validar solape de períodos para el mismo vehículo
        solapados = ContratoPeriodo.objects.filter(
            vehiculo=self.vehiculo,
            fecha_inicio__lt=self.fecha_fin,
            fecha_fin__gt=self.fecha_inicio
        ).exclude(pk=self.pk)
        if solapados.exists():
            raise ValidationError("Ya existe un período para este vehículo que se solapa con las fechas indicadas.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.vehiculo} ({self.fecha_inicio:%d/%m/%Y} - {self.fecha_fin:%d/%m/%Y}) en {self.contrato}"

# ---- Extras ----
class Extra(models.Model):
    """Ítems adicionales para contratos: GPS, silla, seguro, etc."""
    nombre = models.CharField(max_length=64, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Extra"
        verbose_name_plural = "Extras"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} (${self.precio})"

# ---- ContratoVehiculo ----
class ContratoVehiculo(models.Model):
    """Historial de vehículos asociados a un contrato (por reemplazos, períodos, etc)."""
    MODO_CHOICES = [
        ('PRINCIPAL', 'Principal'),
        ('REEMPLAZO', 'Reemplazo'),
    ]
    contrato = models.ForeignKey('Contrato', on_delete=models.CASCADE, related_name='vehiculos_historial')
    vehiculo = models.ForeignKey('flota.Vehiculo', on_delete=models.PROTECT, related_name='contratos_historial')
    es_principal = models.BooleanField(default=False)
    modo = models.CharField(max_length=16, choices=MODO_CHOICES, default='PRINCIPAL')
    fecha_desde = models.DateTimeField(default=timezone.now)
    fecha_hasta = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Historial de Vehículo en Contrato"
        verbose_name_plural = "Historial de Vehículos en Contrato"
        ordering = ['contrato', '-fecha_desde']

    def __str__(self):
        return f"{self.vehiculo} ({self.get_modo_display()}) para {self.contrato}"

# ---- Entrega ----
class Entrega(models.Model):
    """Datos de entrega y devolución de vehículos: sucursal o delivery."""
    contrato = models.OneToOneField('Contrato', on_delete=models.CASCADE, related_name='entrega')
    is_delivery = models.BooleanField("¿Entrega a domicilio?", default=False)
    direccion_entrega = models.CharField(max_length=255, blank=True, null=True)
    direccion_devolucion = models.CharField(max_length=255, blank=True, null=True)
    chofer = models.CharField(max_length=100, blank=True, null=True)
    delivery_cost = models.DecimalField("Costo de delivery", max_digits=10, decimal_places=2, default=0, blank=True, null=True)

    class Meta:
        verbose_name = "Entrega"
        verbose_name_plural = "Entregas"

    def __str__(self):
        return f"Entrega para {self.contrato} ({'Delivery' if self.is_delivery else 'Sucursal'})"

# ---- Checklist ----
class Checklist(models.Model):
    """Checklist de revisión para entrega, devolución o reemplazo de vehículo."""
    TIPO_EVENTO_CHOICES = [
        ('ENTREGA', 'Entrega'),
        ('REEMPLAZO', 'Reemplazo'),
        ('DEVOLUCION', 'Devolución'),
    ]
    contrato = models.ForeignKey('Contrato', on_delete=models.CASCADE, related_name='checklists')
    vehiculo = models.ForeignKey('flota.Vehiculo', on_delete=models.PROTECT, related_name='checklists')
    tipo_evento = models.CharField(max_length=16, choices=TIPO_EVENTO_CHOICES)
    fecha = models.DateTimeField(default=timezone.now)
    kilometraje = models.PositiveIntegerField()
    observaciones = models.TextField(blank=True, null=True)
    fotos = models.ImageField(upload_to='checklists/fotos/', blank=True, null=True)
    # Si quieres varias fotos, puedes crear un modelo aparte y usar ManyToMany.

    class Meta:
        verbose_name = "Checklist"
        verbose_name_plural = "Checklists"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.get_tipo_evento_display()} - {self.vehiculo} ({self.fecha.date()})"

# ---- Constantes de factura/nota ----
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

# ---- Cliente ----
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

# ---- Reserva ----
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
    vehiculo = models.ForeignKey(
        'flota.Vehiculo',
        on_delete=models.PROTECT,
        related_name='reservas',
        verbose_name="Vehículo",
        null=True,
        blank=True
    )
    fecha_inicio = models.DateTimeField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateTimeField(verbose_name="Fecha de Fin")
    fecha_reserva = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Reserva")
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
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")

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

# ---- Contrato ----
class Contrato(models.Model):
    def get_vehiculos_disponibles(self, fecha_inicio=None, fecha_fin=None):
        """
        Devuelve queryset de vehículos disponibles para este contrato.
        Si se proveen fechas, excluye vehículos ocupados en periodos solapados.
        Incluye vehículos DISPONIBLE y LIBRE (con advertencia si tiene subestado).
        """
        from apps.flota.models import Vehiculo
        qs = Vehiculo.objects.filter(estado_general__in=['DISPONIBLE', 'LIBRE'])
        if fecha_inicio and fecha_fin:
            ocupados = ContratoPeriodo.objects.filter(
                fecha_inicio__lt=fecha_fin,
                fecha_fin__gt=fecha_inicio
            ).values_list('vehiculo_id', flat=True)
            qs = qs.exclude(id__in=ocupados)
        return qs

    # --- campos y choices según tu versión actual ---
    ESTADO_CHOICES = [
        ('POR_FIRMAR', 'Por firmar'),
        ('ACTIVO', 'Activo'),
        ('FINALIZADO', 'Finalizado'),
        ('CANCELADO', 'Cancelado'),
    ]

    reserva = models.OneToOneField(
        'Reserva',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contrato',
        verbose_name="Reserva"
    )
    cliente = models.ForeignKey(
        'Cliente',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='contratos',
        verbose_name="Cliente directo"
    )
    vehiculo = models.ForeignKey(
        'flota.Vehiculo',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='contratos'
    )
    numero_contrato = models.CharField(max_length=20, unique=True, blank=True)
    fecha_inicio = models.DateTimeField(verbose_name="Fecha inicio arriendo", null=True, blank=True)
    fecha_fin = models.DateTimeField(verbose_name="Fecha fin arriendo", null=True, blank=True)
    fecha_firma = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de firma")
    estado = models.CharField(
        max_length=20,
        default='POR_FIRMAR',
        choices=ESTADO_CHOICES
    )
    terminos_condiciones = models.TextField(blank=True)
    documento_pdf = models.FileField(upload_to='contratos/', null=True, blank=True)
    extras = models.ManyToManyField('Extra', blank=True, related_name='contratos')

    tarifa_diaria = models.DecimalField(
        "Tarifa diaria",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Tarifa diaria base del arriendo (puede venir del grupo o del vehículo, editable por el usuario)."
    )
    descuento_porcentaje = models.DecimalField(
        "Descuento (%)",
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Porcentaje de descuento aplicado al subtotal (0-100%)."
    )
    garantia = models.DecimalField(
        "Garantía",
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Monto de garantía exigida en el contrato."
    )
    monto_total = models.DecimalField(
        "Monto total del contrato",
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total final a pagar por el contrato, calculado automáticamente."
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Si hay vehículo asignado y el contrato está activo o por firmar, marcar el vehículo como EN_ARRIENDO
        if self.vehiculo and self.estado in ['ACTIVO', 'POR_FIRMAR']:
            if self.vehiculo.estado_general != 'EN_ARRIENDO':
                self.vehiculo.estado_general = 'EN_ARRIENDO'
                self.vehiculo.save(update_fields=['estado_general'])

    def __str__(self):
        return self.numero_contrato or f"Contrato #{self.id}"

    @property
    def cliente_visible(self):
        if self.reserva and self.reserva.cliente:
            return self.reserva.cliente
        return self.cliente

    @property
    def vehiculo_visible(self):
        if self.reserva and self.reserva.vehiculo:
            return self.reserva.vehiculo
        return self.vehiculo

    @property
    def puede_editar_direccion_devolucion(self):
        return self.estado == 'ACTIVO'

# ---- Factura ----
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

# ---- Nota ----
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
