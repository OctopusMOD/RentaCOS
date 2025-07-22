# Estado para OrdenIngreso
class EstadoOI:
    ABIERTA = 'ABIERTA'
    CANCELADA = 'CANCELADA'
    CHOICES = [
        (ABIERTA, 'Abierta'),
        (CANCELADA, 'Cancelada')
    ]
from django.conf import settings
from django.db import models
from django.utils import timezone
from apps.flota.models import Vehiculo


# --- Estado para Taller ---
class EstadoTaller:
    ACTIVO = 'ACTIVO'
    INACTIVO = 'INACTIVO'
    REVISION = 'REVISION'
    CHOICES = [
        (ACTIVO, 'Activo'),
        (INACTIVO, 'Inactivo'),
        (REVISION, 'En revisión')
    ]

# --- Modelo Taller extendido ---
class Taller(models.Model):
    # Información legal/tributaria
    razon_social = models.CharField("Razón Social", max_length=128)
    nombre = models.CharField("Nombre de fantasía / comercial", max_length=128)
    rut = models.CharField("RUT de la empresa", max_length=20)
    giro_comercial = models.CharField("Giro comercial", max_length=128, blank=True, null=True)
    direccion = models.CharField("Dirección", max_length=256)
    comuna = models.CharField("Comuna", max_length=64)
    region = models.CharField("Región", max_length=64)
    telefono = models.CharField("Teléfono de contacto", max_length=32)
    email = models.EmailField("Correo de contacto", blank=True, null=True)
    representante_legal = models.CharField("Representante legal", max_length=128, blank=True, null=True)
    rut_representante = models.CharField("RUT representante legal", max_length=20, blank=True, null=True)

    # Información operativa
    TIPOS_SERVICIO_CHOICES = [
        ('mecanica', 'Mecánica general'),
        ('electricidad', 'Electricidad'),
        ('frenos', 'Frenos'),
        ('suspension', 'Suspensión'),
        ('aire', 'Aire acondicionado'),
        ('lubricentro', 'Lubricentro (aceite y filtros)'),
        ('otro', 'Otro'),
    ]
    tipos_servicio = models.CharField(
        "Tipos de servicios ofrecidos",
        max_length=200,
        help_text="Ejemplo: mecánica general, electricidad, frenos, etc. (separados por coma)"
    )
    dias_horarios = models.CharField("Días y horarios de atención", max_length=128)
    sitio_web = models.URLField("Sitio web", blank=True, null=True)
    redes_sociales = models.CharField("Redes sociales", max_length=256, blank=True, null=True)
    logo = models.ImageField("Logo/foto del taller", upload_to="talleres/logos/", blank=True, null=True)
    ubicacion_mapa = models.CharField("Ubicación mapa (embed o link)", max_length=512, blank=True, null=True)

    # Trazabilidad interna
    usuario_creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="talleres_creados"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(
        "Estado",
        max_length=16,
        choices=EstadoTaller.CHOICES,
        default=EstadoTaller.ACTIVO
    )

    def __str__(self):
        return self.nombre

class TipoMantenimiento(models.Model):
    nombre = models.CharField(max_length=64, unique=True)
    es_preventivo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


# Estados de mantenimiento
class EstadoMantenimiento:
    PENDIENTE = 'PENDIENTE'
    EN_PROCESO = 'EN_PROCESO'
    COMPLETADO = 'COMPLETADO'
    ANULADO = 'ANULADO'
    CHOICES = [
        (PENDIENTE, 'Pendiente'),
        (EN_PROCESO, 'En proceso'),
        (COMPLETADO, 'Completado'),
        (ANULADO, 'Anulado'),
    ]

class OrdenMantenimiento(models.Model):
    numero_orden = models.CharField(
        max_length=10, unique=True, blank=True, null=True, verbose_name="Nº Orden"
    )
    vehiculo = models.ForeignKey('flota.Vehiculo', on_delete=models.PROTECT)
    kilometraje_ingreso_mantenimiento = models.PositiveIntegerField()
    taller = models.ForeignKey('mantenimiento.Taller', on_delete=models.PROTECT)
    tipo = models.ForeignKey('mantenimiento.TipoMantenimiento', on_delete=models.PROTECT)
    estado = models.CharField(max_length=20, choices=EstadoMantenimiento.CHOICES, default=EstadoMantenimiento.PENDIENTE)
    fecha_ingreso = models.DateField()
    fecha_salida = models.DateField(blank=True, null=True)
    descripcion_problema = models.TextField(blank=True, default="", verbose_name="Observaciones del Ingreso")

    def save(self, *args, **kwargs):
        if not self.numero_orden:
            last = OrdenMantenimiento.objects.order_by('-id').first()
            next_number = 1 if not last or not last.numero_orden else int(last.numero_orden.split('-')[1]) + 1
            self.numero_orden = f"OT-{next_number:02d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero_orden} - {self.vehiculo}"

class TrabajoRealizado(models.Model):
    COMPONENTES_CHOICES = [
        ('motor', 'Motor'),
        ('transmision', 'Transmisión'),
        ('chasis', 'Chasis'),
        ('suspension', 'Suspensión'),
        ('frenos', 'Frenos'),
        ('direccion', 'Dirección'),
        ('electrico', 'Sistema Eléctrico'),
        ('carroceria', 'Carrocería'),
        ('neumaticos', 'Neumáticos'),
        ('escape', 'Sistema de Escape'),
        ('otro', 'Otro'),
    ]
    orden = models.ForeignKey(OrdenMantenimiento, related_name='trabajos', on_delete=models.CASCADE)
    codigo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255)
    componente = models.CharField(max_length=100, choices=COMPONENTES_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    unidades = models.PositiveIntegerField()
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, default=0)

    def save(self, *args, **kwargs):
        self.valor_total = self.valor * self.unidades
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} {self.descripcion}"

class RepuestoUtilizado(models.Model):
    orden = models.ForeignKey(OrdenMantenimiento, related_name='repuestos', on_delete=models.CASCADE)
    codigo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    unidades = models.PositiveIntegerField()
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, default=0)

    def save(self, *args, **kwargs):
        self.valor_total = self.valor * self.unidades
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} {self.descripcion}"

class OrdenIngreso(models.Model):
    numero_orden = models.CharField(max_length=10, unique=True, blank=True)
    vehiculo = models.ForeignKey('flota.Vehiculo', on_delete=models.CASCADE)
    fecha_ingreso = models.DateTimeField(default=timezone.now)
    tipo_mantenimiento = models.ForeignKey('mantenimiento.TipoMantenimiento', on_delete=models.CASCADE)
    taller = models.ForeignKey('mantenimiento.Taller', on_delete=models.PROTECT, null=True, blank=True)
    kilometraje_actual = models.PositiveIntegerField(null=True, blank=True, verbose_name="Kilometraje actual")
    estado = models.CharField(max_length=20, choices=EstadoOI.CHOICES, default=EstadoOI.ABIERTA)
    creado = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.numero_orden:
            last = OrdenIngreso.objects.all().order_by('-id').first()
            next_number = 1
            if last and last.numero_orden:
                try:
                    next_number = int(last.numero_orden.split('-')[1]) + 1
                except (IndexError, ValueError):
                    pass
            self.numero_orden = f'OI-{next_number:02d}'
        super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.numero_orden} - {self.vehiculo}'

class TrabajoSolicitado(models.Model):
    orden_ingreso = models.ForeignKey(OrdenIngreso, related_name='trabajos', on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=255)

    def __str__(self):
        return self.descripcion