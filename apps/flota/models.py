from django.conf import settings
from django.db import models
from datetime import date, timedelta

class Marca(models.Model):
    nombre = models.CharField(max_length=64, unique=True)
    pais_origen = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return self.nombre

class TipoCarroceria(models.Model):
    nombre = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.nombre

class ModeloVehiculo(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, related_name='modelos')
    nombre = models.CharField(max_length=64)
    anio = models.PositiveIntegerField("Año de modelo", blank=True, null=True)
    tipo_carroceria = models.ForeignKey(TipoCarroceria, on_delete=models.PROTECT, related_name='modelos')

    class Meta:
        unique_together = ('marca', 'nombre', 'anio')

    def __str__(self):
        return f"{self.marca} {self.nombre} {self.anio or ''}"

class GrupoVehiculo(models.Model):
    nombre = models.CharField(max_length=64, unique=True)
    descripcion = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return self.nombre

class Vehiculo(models.Model):
    TRANSMISION_CHOICES = [
        ('MANUAL', 'Manual'),
        ('AUTOMATICA', 'Automática'),
    ]
    COMBUSTIBLE_CHOICES = [
        ('BENCINA', 'Bencina'),
        ('DIESEL', 'Diésel'),
        ('ELECTRICO', 'Eléctrico'),
        ('HIBRIDO', 'Híbrido'),
        ('GNC', 'Gas Natural'),
        ('GLP', 'Gas Licuado'),
        ('OTRO', 'Otro'),
    ]
    ESTADO_GENERAL_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('EN_ARRIENDO', 'En arriendo'),
        ('EN_REEMPLAZO', 'En reemplazo'),
        ('DADO_BAJA', 'Dado de baja'),
        ('LIBRE', 'Libre'),
    ]
    SUBESTADO_CHOICES = [
        ('NINGUNO', 'Sin subestado'),
        ('EN_REPARACION', 'En reparación'),
        ('FUERA_SERVICIO', 'Fuera de servicio'),
        ('EN_EQUIPAMIENTO', 'En equipamiento'),
        ('EN_TRANSITO', 'En tránsito'),
        ('MANTENIMIENTO_ATRASADO', 'Mantenimiento atrasado'),
        ('PROX_MANTENIMIENTO', 'Próx. a mantenimiento'),
        ('EN_OBSERVACION', 'En observación'),
    ]
    TRACCION_CHOICES = [
        ('4x2', '4x2'),
        ('4x4', '4x4'),
        ('AWD', 'AWD'),
        ('OTRO', 'Otro'),
    ]
    TENENCIA_CHOICES = [
        ('PROPIO', 'Propio'),
        ('SUBARRENDADO', 'Subarrendado'),
        ('LEASING', 'Leasing'),
        ('CLIENTE', 'Cliente'),
        ('OTRO', 'Otro'),
    ]

    modelo = models.ForeignKey(ModeloVehiculo, on_delete=models.PROTECT, related_name='vehiculos')
    grupo = models.ForeignKey(GrupoVehiculo, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehiculos')
    patente = models.CharField(max_length=12, unique=True)
    vin = models.CharField("VIN/Chasis", max_length=32, unique=True)
    traccion = models.CharField(max_length=16, choices=TRACCION_CHOICES, default='4x2')
    tenencia = models.CharField(max_length=16, choices=TENENCIA_CHOICES, default='PROPIO')
    anio_fabricacion = models.PositiveIntegerField(blank=True, null=True)
    color = models.CharField(max_length=32)
    transmision = models.CharField(max_length=16, choices=TRANSMISION_CHOICES)
    combustible = models.CharField(max_length=16, choices=COMBUSTIBLE_CHOICES)
    capacidad = models.PositiveIntegerField(help_text="Capacidad de carga (kg) o pasajeros", blank=True, null=True)
    numero_asientos = models.PositiveSmallIntegerField(blank=True, null=True)
    estado_general = models.CharField(
        max_length=20,
        choices=ESTADO_GENERAL_CHOICES,
        default='LIBRE',
        verbose_name='Estado general'
    )
    subestado = models.CharField(
        max_length=30,
        choices=SUBESTADO_CHOICES,
        default='NINGUNO',
        verbose_name='Subestado'
    )
    kilometraje_actual = models.PositiveIntegerField(default=0)
    proximo_mantenimiento = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Kilometraje al que corresponde el próximo mantenimiento"
    )
    observaciones = models.TextField(blank=True, null=True)

    # Documentación legal
    fecha_vencimiento_soap = models.DateField("Vencimiento SOAP", blank=True, null=True)
    archivo_soap = models.FileField(upload_to='vehiculos/soap/', null=True, blank=True)
    fecha_vencimiento_rev_tecnica = models.DateField("Vencimiento Rev. Técnica", blank=True, null=True)
    archivo_rev_tecnica = models.FileField(upload_to='vehiculos/rev_tecnica/', blank=True, null=True)
    fecha_vencimiento_permiso_circulacion = models.DateField("Vencimiento Permiso Circulación", blank=True, null=True)
    archivo_permiso_circulacion = models.FileField(upload_to='vehiculos/permiso_circulacion/', blank=True, null=True)
    fecha_vencimiento_homologacion = models.DateField("Vencimiento Homologación", blank=True, null=True)
    archivo_homologacion = models.FileField(upload_to='vehiculos/homologacion/', blank=True, null=True)

    def __str__(self):
        return f"{self.patente} ({self.modelo})"

    def documento_estado(self, fecha_vencimiento, dias_alerta=30):
        if not fecha_vencimiento:
            return None
        hoy = date.today()
        if fecha_vencimiento < hoy:
            return 'vencido'
        elif fecha_vencimiento <= hoy + timedelta(days=dias_alerta):
            return 'por_vencer'
        else:
            return 'ok'

    def estado_soap(self):
        return self.documento_estado(self.fecha_vencimiento_soap)

    def estado_rev_tecnica(self):
        return self.documento_estado(self.fecha_vencimiento_rev_tecnica)

    def estado_permiso_circulacion(self):
        return self.documento_estado(self.fecha_vencimiento_permiso_circulacion)

    def estado_homologacion(self):
        return self.documento_estado(self.fecha_vencimiento_homologacion)

    def get_estado_display(self):
        """
        Retorna el estado general y subestado formateados para mostrar al usuario.
        """
        if self.subestado and self.subestado != 'NINGUNO':
            return f"{self.get_estado_general_display()} ({self.get_subestado_display()})"
        return self.get_estado_general_display()

class DocumentoVehiculo(models.Model):
    TIPO_CHOICES = [
        ('SOAP', 'SOAP'),
        ('REV_TECNICA', 'Revisión Técnica'),
        ('PERMISO_CIRCULACION', 'Permiso de Circulación'),
        ('HOMOLOGACION', 'Homologación'),
        ('OTRO', 'Otro'),
    ]
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField(max_length=32, choices=TIPO_CHOICES, default='OTRO')
    descripcion = models.CharField(max_length=128, blank=True)
    fecha_emision = models.DateField(blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    archivo = models.FileField(upload_to='vehiculos/documentos/', blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_tipo_display()} {self.vehiculo.patente}"

class KilometrajeVehiculo(models.Model):
    TIPO_EVENTO_CHOICES = [
        ('LECTURA', 'Lectura periódica'),
        ('ENTREGA', 'Entrega a cliente'),
        ('DEVOLUCION', 'Devolución de cliente'),
        ('MANTENIMIENTO', 'Ingreso a mantenimiento'),
        ('SALIDA_MANTENIMIENTO', 'Salida de mantenimiento'),
        ('AJUSTE', 'Ajuste administrativo'),
    ]

    vehiculo = models.ForeignKey('Vehiculo', on_delete=models.CASCADE, related_name='historial_kilometraje')
    fecha = models.DateTimeField(auto_now_add=True)
    kilometraje = models.PositiveIntegerField()
    tipo_evento = models.CharField(max_length=25, choices=TIPO_EVENTO_CHOICES)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    observaciones = models.TextField(blank=True)
    cliente = models.ForeignKey('alquiler.Cliente', null=True, blank=True, on_delete=models.SET_NULL)
    estado_general = models.CharField(max_length=20, blank=True, editable=False)
    subestado = models.CharField(max_length=30, blank=True, editable=False)

    class Meta:
        ordering = ['-fecha']

    def save(self, *args, **kwargs):
        self.estado_general = self.vehiculo.estado_general
        self.subestado = self.vehiculo.subestado
        if self.vehiculo.estado_general == 'EN_ARRIENDO':
            arriendo_activo = getattr(self.vehiculo, 'arriendo_activo', None)
            if arriendo_activo:
                self.cliente = arriendo_activo.cliente
            else:
                self.cliente = None
        else:
            self.cliente = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.vehiculo} - {self.kilometraje} km ({self.get_tipo_evento_display()}) {self.fecha.date()}"