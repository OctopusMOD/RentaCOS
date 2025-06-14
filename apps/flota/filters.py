import django_filters
from .models import Vehiculo, Marca, ModeloVehiculo, GrupoVehiculo, KilometrajeVehiculo
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from django.db import models

User = get_user_model()

class VehiculoFilter(django_filters.FilterSet):
    marca = django_filters.ModelChoiceFilter(
        queryset=Marca.objects.all(),
        field_name='modelo__marca',
        label='Marca'
    )
    modelo = django_filters.ModelChoiceFilter(
        queryset=ModeloVehiculo.objects.all(),
        field_name='modelo',
        label='Modelo'
    )
    grupo = django_filters.ModelChoiceFilter(
        queryset=GrupoVehiculo.objects.all(),
        label='Grupo'
    )
    patente = django_filters.CharFilter(lookup_expr='icontains', label='Patente')

    ALERTA_CHOICES = (
        ('', 'Todos'),
        ('por_vencer', 'Documento por vencer'),
        ('vencido', 'Documento vencido'),
    )
    alerta_documentos = django_filters.ChoiceFilter(
        label="Alerta documentos",
        choices=ALERTA_CHOICES,
        method='filter_alerta_documentos',
        widget=django_filters.widgets.LinkWidget
    )

    estado_general = django_filters.ChoiceFilter(
        label='Estado general',
        choices=Vehiculo.ESTADO_GENERAL_CHOICES,
        empty_label='Todos'
    )
    subestado = django_filters.ChoiceFilter(
        label='Subestado',
        choices=Vehiculo.SUBESTADO_CHOICES,
        empty_label='Todos'
    )

    class Meta:
        model = Vehiculo
        fields = ['grupo', 'modelo', 'estado_general', 'subestado', 'alerta_documentos']

    def filter_alerta_documentos(self, queryset, name, value):
        hoy = date.today()
        dias_alerta = 30  # puedes parametrizar esto
        if value == 'por_vencer':
            return queryset.filter(
                (
                    models.Q(fecha_vencimiento_soap__gt=hoy) &
                    models.Q(fecha_vencimiento_soap__lte=hoy + timedelta(days=dias_alerta))
                ) |
                (
                    models.Q(fecha_vencimiento_rev_tecnica__gt=hoy) &
                    models.Q(fecha_vencimiento_rev_tecnica__lte=hoy + timedelta(days=dias_alerta))
                ) |
                (
                    models.Q(fecha_vencimiento_permiso_circulacion__gt=hoy) &
                    models.Q(fecha_vencimiento_permiso_circulacion__lte=hoy + timedelta(days=dias_alerta))
                ) |
                (
                    models.Q(fecha_vencimiento_homologacion__gt=hoy) &
                    models.Q(fecha_vencimiento_homologacion__lte=hoy + timedelta(days=dias_alerta))
                )
            )
        elif value == 'vencido':
            return queryset.filter(
                models.Q(fecha_vencimiento_soap__lt=hoy) |
                models.Q(fecha_vencimiento_rev_tecnica__lt=hoy) |
                models.Q(fecha_vencimiento_permiso_circulacion__lt=hoy) |
                models.Q(fecha_vencimiento_homologacion__lt=hoy)
            )
        return queryset

class KilometrajeVehiculoFilter(django_filters.FilterSet):
    vehiculo__patente = django_filters.CharFilter(
        field_name='vehiculo__patente',
        label='Patente',
        lookup_expr='icontains'
    )
    vehiculo = django_filters.ModelChoiceFilter(
        queryset=Vehiculo.objects.all(),
        label="Vehículo"
    )
    tipo_evento = django_filters.ChoiceFilter(
        choices=KilometrajeVehiculo.TIPO_EVENTO_CHOICES,
        label="Tipo de evento",
        empty_label="Todos"
    )
    usuario = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        label="Usuario"
    )
    fecha = django_filters.DateFromToRangeFilter(
        label="Rango de fecha",
        widget=django_filters.widgets.RangeWidget(attrs={'type': 'date', 'class': 'form-control'})
    )
    kilometraje = django_filters.RangeFilter(
        label="Rango Kilometraje",
        widget=django_filters.widgets.RangeWidget(attrs={'class': 'form-control', 'placeholder': 'km'})
    )

    class Meta:
        model = KilometrajeVehiculo
        fields = ['vehiculo', 'vehiculo__patente', 'tipo_evento', 'usuario', 'fecha', 'kilometraje']