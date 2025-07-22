from django.contrib import admin
from .models import (
    TipoMantenimiento,
    OrdenMantenimiento,
    Taller,
    OrdenIngreso,
    TrabajoSolicitado,
    TrabajoRealizado,
    RepuestoUtilizado,
)

@admin.register(Taller)
class TallerAdmin(admin.ModelAdmin):
    list_display = (
        "nombre", "razon_social", "rut", "direccion", "telefono", "estado",
        "usuario_creador", "fecha_creacion"
    )
    search_fields = ("nombre", "razon_social", "rut", "direccion", "telefono", "comuna", "region")
    list_filter = ("estado", "region", "comuna")
    readonly_fields = ("fecha_creacion", "fecha_modificacion", "usuario_creador")
    fieldsets = (
        ("Información Legal y Tributaria", {
            "fields": (
                "razon_social", "nombre", "rut", "giro_comercial",
                "direccion", "comuna", "region", "telefono", "email",
                "representante_legal", "rut_representante"
            )
        }),
        ("Información Operativa", {
            "fields": (
                "tipos_servicio", "dias_horarios", "sitio_web", "redes_sociales",
                "logo", "ubicacion_mapa"
            )
        }),
        ("Trazabilidad Interna", {
            "fields": ("estado", "usuario_creador", "fecha_creacion", "fecha_modificacion")
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.usuario_creador:
            obj.usuario_creador = request.user
        super().save_model(request, obj, form, change)

@admin.register(TipoMantenimiento)
class TipoMantenimientoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "es_preventivo")
    list_filter = ("es_preventivo",)
    search_fields = ("nombre",)

@admin.register(OrdenMantenimiento)
class OrdenMantenimientoAdmin(admin.ModelAdmin):
    list_display = ("id", "numero_orden", "vehiculo", "taller", "tipo", "estado", "fecha_ingreso", "fecha_salida")
    list_filter = ("estado", "tipo", "taller", "fecha_ingreso", "fecha_salida")
    search_fields = ("vehiculo__patente", "descripcion_problema")
    date_hierarchy = "fecha_ingreso"
    autocomplete_fields = ("vehiculo",)

@admin.register(TrabajoRealizado)
class TrabajoRealizadoAdmin(admin.ModelAdmin):
    list_display = ("orden", "codigo", "descripcion", "componente", "valor", "unidades", "valor_total")
    search_fields = ("descripcion", "codigo", "orden__numero_orden")

@admin.register(RepuestoUtilizado)
class RepuestoUtilizadoAdmin(admin.ModelAdmin):
    list_display = ("orden", "codigo", "descripcion", "valor", "unidades", "valor_total")
    search_fields = ("descripcion", "codigo", "orden__numero_orden")

class TrabajoSolicitadoInline(admin.TabularInline):
    model = TrabajoSolicitado
    extra = 1

@admin.register(OrdenIngreso)
class OrdenIngresoAdmin(admin.ModelAdmin):
    list_display = ("numero_orden", "vehiculo", "fecha_ingreso", "tipo_mantenimiento", "creado")
    search_fields = ("numero_orden", "vehiculo__patente")
    list_filter = ("tipo_mantenimiento", "fecha_ingreso")
    autocomplete_fields = ("vehiculo", "tipo_mantenimiento")
    inlines = [TrabajoSolicitadoInline]

@admin.register(TrabajoSolicitado)
class TrabajoSolicitadoAdmin(admin.ModelAdmin):
    list_display = ("orden_ingreso", "descripcion")
    search_fields = ("descripcion", "orden_ingreso__numero_orden")