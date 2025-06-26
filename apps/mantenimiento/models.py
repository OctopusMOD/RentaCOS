from django.db import models
from apps.flota.models import Vehiculo

class Taller(models.Model):
    nombre = models.CharField(max_length=128, unique=True)
    direccion = models.CharField(max_length=256, blank=True, null=True)
    telefono = models.CharField(max_length=32, blank=True, null=True)
    contacto = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.nombre

class TipoMantenimiento(models.Model):
    nombre = models.CharField(max_length=64, unique=True)
    es_preventivo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({'Preventivo' if self.es_preventivo else 'Correctivo'})"

class OrdenMantenimiento(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROCESO', 'En proceso'),
        ('COMPLETADO', 'Completado'),
        ('CANCELADO', 'Cancelado'),
    ]

    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name="ordenes_mantenimiento"
    )
    taller = models.ForeignKey(
        Taller,
        on_delete=models.PROTECT
    )
    tipo = models.ForeignKey(
        TipoMantenimiento,
        on_delete=models.SET_NULL,
        null=True
    )
    fecha_ingreso = models.DateField(verbose_name="Fecha de entrada al taller")
    fecha_salida = models.DateField(blank=True, null=True, verbose_name="Fecha de salida del taller")
    estado = models.CharField(max_length=16, choices=ESTADO_CHOICES, default='PENDIENTE')
    descripcion_problema = models.TextField(blank=True, null=True)
    diagnostico = models.TextField(blank=True, null=True)
    tecnico_responsable = models.CharField(max_length=64, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Orden #{self.id} - {self.vehiculo.patente} - {self.estado}"

class ItemRepuesto(models.Model):
    nombre = models.CharField(max_length=64)
    codigo = models.CharField(max_length=32, unique=True)
    cantidad_stock = models.PositiveIntegerField(default=0)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class ConsumoRepuesto(models.Model):
    orden = models.ForeignKey(OrdenMantenimiento, on_delete=models.CASCADE, related_name='repuestos_utilizados')
    repuesto = models.ForeignKey(ItemRepuesto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.repuesto.nombre} x{self.cantidad} (Orden #{self.orden.id})"

class TrabajoRealizado(models.Model):
    orden = models.ForeignKey('OrdenMantenimiento', on_delete=models.CASCADE, related_name='trabajos')
    codigo = models.CharField(max_length=32, blank=True)
    descripcion = models.CharField(max_length=256)
    unidades = models.DecimalField(max_digits=6, decimal_places=2)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def total(self):
        return self.unidades * self.valor_unitario

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"