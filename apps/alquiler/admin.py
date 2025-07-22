from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from django.utils import timezone
from .models import Cliente, Reserva, Contrato, Factura, Nota, Extra

@admin.register(Extra)
class ExtraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)
    fields = ('nombre', 'descripcion', 'precio', 'activo')

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_empresa_o_contacto', 'tipo_cliente', 'documento',
                   'telefono_principal', 'email_principal', 'ciudad', 'activo',
                   'total_reservas')
    list_filter = ('activo', 'tipo_cliente', 'region', 'ciudad', 'fecha_registro')
    search_fields = ('razon_social', 'nombre_comercial', 'rut_empresa',
                    'nombre_contacto', 'apellidos_contacto', 'email_empresa',
                    'email_contacto')
    ordering = ('-fecha_registro',)
    date_hierarchy = 'fecha_registro'

    fieldsets = (
        ('Tipo de Cliente', {
            'fields': ('tipo_cliente', 'activo')
        }),
        ('Información Empresarial', {
            'fields': (
                ('razon_social', 'nombre_comercial'),
                ('rut_empresa', 'giro')
            ),
            'classes': ('empresa-fields',)
        }),
        ('Contacto Principal', {
            'fields': (
                ('nombre_contacto', 'apellidos_contacto'),
                'cargo_contacto',
                ('tipo_documento', 'numero_documento')
            )
        }),
        ('Información de Contacto', {
            'fields': (
                ('telefono_empresa', 'telefono_contacto'),
                ('email_empresa', 'email_contacto')
            )
        }),
        ('Ubicación', {
            'fields': (
                'direccion',
                ('comuna', 'ciudad', 'region'),
                'codigo_postal'
            )
        }),
        ('Información Adicional', {
            'fields': ('sitio_web', 'observaciones'),
            'classes': ('collapse',)
        }),
    )

    def nombre_empresa_o_contacto(self, obj):
        if obj.tipo_cliente == 'EMPRESA':
            return obj.razon_social
        return f"{obj.nombre_contacto} {obj.apellidos_contacto}"
    nombre_empresa_o_contacto.short_description = "Nombre"
    nombre_empresa_o_contacto.admin_order_field = 'razon_social'

    def documento(self, obj):
        if obj.tipo_cliente == 'EMPRESA':
            return f"RUT: {obj.rut_empresa}"
        return f"{obj.get_tipo_documento_display()}: {obj.numero_documento}"
    documento.short_description = "Documento"

    def telefono_principal(self, obj):
        telefono = obj.telefono_empresa if obj.tipo_cliente == 'EMPRESA' else obj.telefono_contacto
        return format_html('<a href="tel:{}">{}</a>', telefono, telefono)
    telefono_principal.short_description = "Teléfono"

    def email_principal(self, obj):
        email = obj.email_empresa if obj.tipo_cliente == 'EMPRESA' else obj.email_contacto
        return format_html('<a href="mailto:{}">{}</a>', email, email)
    email_principal.short_description = "Email"

    def total_reservas(self, obj):
        count = obj.reservas.count()
        url = reverse('admin:alquiler_reserva_changelist') + f'?cliente__id={obj.id}'
        return format_html('<a href="{}">{} reserva(s)</a>', url, count)
    total_reservas.short_description = "Reservas"

    class Media:
        js = ('js/cliente_admin.js',)

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_inicio', 'fecha_fin',
                   'estado', 'monto_total', 'tiene_contrato', 'tiene_factura')
    list_filter = ('estado', 'fecha_inicio', 'fecha_fin')
    search_fields = ('cliente__razon_social', 'cliente__nombre_contacto',
                    'cliente__apellidos_contacto')
    date_hierarchy = 'fecha_inicio'
    readonly_fields = ('fecha_reserva', 'monto_total')
    raw_id_fields = ('cliente',)

    fieldsets = (
        ('Información Principal', {
            'fields': (
                ('cliente',),
                ('fecha_inicio', 'fecha_fin'),
                'estado'
            )
        }),
        ('Detalles Financieros', {
            'fields': ('monto_total',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('fecha_reserva',),
            'classes': ('collapse',)
        })
    )

    def tiene_contrato(self, obj):
        if hasattr(obj, 'contrato'):
            url = reverse('admin:alquiler_contrato_change', args=[obj.contrato.id])
            return format_html('<a href="{}">Ver contrato</a>', url)
        return format_html('<span class="text-danger">Sin contrato</span>')
    tiene_contrato.short_description = "Contrato"
    tiene_contrato.boolean = True

    def tiene_factura(self, obj):
        contrato = getattr(obj, 'contrato', None)
        if contrato and hasattr(contrato, 'factura'):
            url = reverse('admin:alquiler_factura_change', args=[contrato.factura.id])
            return format_html('<a href="{}">Ver factura</a>', url)
        return format_html('<span class="text-danger">Sin factura</span>')
    tiene_factura.short_description = "Factura"
    tiene_factura.boolean = True

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ('numero_contrato', 'reserva', 'cliente', 'fecha_firma',
                   'estado', 'tiene_pdf', 'listar_extras')
    list_filter = ('estado', 'fecha_firma', 'extras')
    search_fields = ('numero_contrato', 'reserva__cliente__razon_social',
                    'reserva__cliente__nombre_contacto')
    date_hierarchy = 'fecha_firma'
    readonly_fields = ('numero_contrato',)
    raw_id_fields = ('reserva',)
    filter_horizontal = ('extras',)

    fieldsets = (
        ('Información del Contrato', {
            'fields': (
                'numero_contrato',
                'reserva',
                'estado',
                'fecha_firma',
                'extras',
            )
        }),
        ('Documentación', {
            'fields': (
                'terminos_condiciones',
                'documento_pdf'
            )
        })
    )

    def cliente(self, obj):
        if obj.reserva:
            cliente = obj.reserva.cliente
            url = reverse('admin:alquiler_cliente_change', args=[cliente.id])
            return format_html('<a href="{}">{}</a>', url, cliente)
        return "-"
    cliente.short_description = "Cliente"

    def tiene_pdf(self, obj):
        if obj.documento_pdf:
            return format_html(
                '<a href="{}" target="_blank">Ver PDF</a>',
                obj.documento_pdf.url
            )
        return format_html('<span class="text-danger">Sin PDF</span>')
    tiene_pdf.short_description = "PDF"

    def listar_extras(self, obj):
        extras = obj.extras.all()
        if extras:
            return ", ".join([str(e) for e in extras])
        return "-"
    listar_extras.short_description = "Extras"

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = (
        'numero_factura',
        'tipo_documento',
        'contrato',
        'fecha_emision',
        'total',
        'estado',
        'rut_receptor',
    )
    list_filter = ('tipo_documento', 'estado', 'fecha_emision')
    search_fields = ('numero_factura', 'contrato__id', 'rut_receptor', 'razon_social_receptor')
    readonly_fields = ('sii_track_id', 'sii_xml')

    fieldsets = (
        ('Información de la Factura', {
            'fields': (
                'numero_factura',
                'contrato',
                'estado'
            )
        }),
        ('Fechas', {
            'fields': (
                'fecha_emision',
                'fecha_vencimiento'
            )
        }),
        ('Montos', {
            'fields': (
                'subtotal',
                'iva',
                'total'
            )
        })
    )

    def cliente(self, obj):
        contrato = obj.contrato
        if contrato and contrato.reserva:
            cliente = contrato.reserva.cliente
            url = reverse('admin:alquiler_cliente_change', args=[cliente.id])
            return format_html('<a href="{}">{}</a>', url, cliente)
        return "-"
    cliente.short_description = "Cliente"

    def dias_vencimiento(self, obj):
        if obj.estado == 'PAGADA':
            return '-'
        dias = (obj.fecha_vencimiento - timezone.now().date()).days
        if dias < 0:
            return format_html(
                '<span class="text-danger">Vencida ({} días)</span>',
                abs(dias)
            )
        return format_html(
            '<span class="text-success">{} días</span>',
            dias
        )
    dias_vencimiento.short_description = "Días para vencer"

@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'tipo', 'factura', 'fecha_emision', 'monto')
    list_filter = ('tipo', 'fecha_emision')
    search_fields = ('numero', 'factura__numero', 'motivo')
    date_hierarchy = 'fecha_emision'