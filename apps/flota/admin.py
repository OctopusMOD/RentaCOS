from django.contrib import admin
from .models import Marca, ModeloVehiculo, Vehiculo, DocumentoVehiculo, KilometrajeVehiculo

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    search_fields = ['nombre']
    list_display = ['nombre', 'pais_origen']

@admin.register(ModeloVehiculo)
class ModeloVehiculoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'marca', 'anio', 'tipo_carroceria']
    list_filter = ['marca', 'anio', 'tipo_carroceria']
    search_fields = ['nombre']

class DocumentoVehiculoInline(admin.TabularInline):
    model = DocumentoVehiculo
    extra = 0

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = [
        'patente', 'modelo', 'color', 'anio_fabricacion', 'transmision', 'combustible',
        'estado_general', 'subestado', 'kilometraje_actual', 'proximo_mantenimiento'
    ]
    list_filter = [
        'modelo__marca', 'modelo', 'combustible', 'transmision', 'estado_general', 'subestado'
    ]
    search_fields = ['patente', 'modelo__nombre', 'modelo__marca__nombre']
    inlines = [DocumentoVehiculoInline]

@admin.register(DocumentoVehiculo)
class DocumentoVehiculoAdmin(admin.ModelAdmin):
    list_display = [
        'tipo', 'vehiculo', 'fecha_emision', 'fecha_vencimiento', 'archivo'
    ]
    list_filter = ['tipo', 'fecha_vencimiento']
    search_fields = ['vehiculo__patente', 'descripcion']

@admin.register(KilometrajeVehiculo)
class KilometrajeVehiculoAdmin(admin.ModelAdmin):
    list_display = ('vehiculo', 'kilometraje', 'tipo_evento', 'fecha', 'usuario', 'cliente', 'estado_general', 'subestado')
    list_filter = ('vehiculo', 'tipo_evento', 'usuario', 'cliente', 'estado_general')
    search_fields = ('vehiculo__patente',)