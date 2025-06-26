from django.contrib import admin
from .models import TipoMantenimiento, OrdenMantenimiento, ItemRepuesto, ConsumoRepuesto, Taller

@admin.register(Taller)
class TallerAdmin(admin.ModelAdmin):
    list_display = ("nombre", "direccion", "telefono", "contacto")
    search_fields = ("nombre", "direccion", "telefono", "contacto")

@admin.register(TipoMantenimiento)
class TipoMantenimientoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "es_preventivo")
    list_filter = ("es_preventivo",)
    search_fields = ("nombre",)

@admin.register(OrdenMantenimiento)
class OrdenMantenimientoAdmin(admin.ModelAdmin):
    list_display = ("id", "vehiculo", "taller", "tipo", "estado", "fecha_ingreso", "fecha_salida", "tecnico_responsable")
    list_filter = ("estado", "tipo", "taller", "fecha_ingreso", "fecha_salida")
    search_fields = ("vehiculo__patente", "tecnico_responsable", "descripcion_problema")
    date_hierarchy = "fecha_ingreso"
    autocomplete_fields = ("vehiculo", "tipo", "taller")
    readonly_fields = ()
    inlines = []

@admin.register(ItemRepuesto)
class ItemRepuestoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "cantidad_stock")
    search_fields = ("nombre", "codigo")
    ordering = ("nombre",)

@admin.register(ConsumoRepuesto)
class ConsumoRepuestoAdmin(admin.ModelAdmin):
    list_display = ("orden", "repuesto", "cantidad")
    search_fields = ("orden__id", "repuesto__nombre")
    autocomplete_fields = ("orden", "repuesto")