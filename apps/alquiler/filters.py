import django_filters
from .models import Reserva, Contrato, Factura, Cliente, ESTADOS_FACTURA

class ReservaFilter(django_filters.FilterSet):
    cliente = django_filters.ModelChoiceFilter(
        queryset=Cliente.objects.all(),
        label="Cliente"
    )
    estado = django_filters.ChoiceFilter(
        choices=Reserva.ESTADO_CHOICES,
        label="Estado"
    )
    fecha_inicio = django_filters.DateFromToRangeFilter(
        label="Rango Fecha Inicio",
        widget=django_filters.widgets.RangeWidget(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = Reserva
        fields = ['cliente', 'estado', 'fecha_inicio']

class ContratoFilter(django_filters.FilterSet):
    cliente = django_filters.ModelChoiceFilter(
        queryset=Cliente.objects.all(),
        label="Cliente",
        field_name="reserva__cliente"
    )
    estado = django_filters.ChoiceFilter(
        choices=Contrato.ESTADO_CHOICES,
        label="Estado"
    )
    fecha_firma = django_filters.DateFromToRangeFilter(
        label="Rango Fecha Firma",
        widget=django_filters.widgets.RangeWidget(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = Contrato
        fields = ['cliente', 'estado', 'fecha_firma']

class FacturaFilter(django_filters.FilterSet):
    cliente = django_filters.ModelChoiceFilter(
        queryset=Cliente.objects.all(),
        label="Cliente",
        field_name="contrato__reserva__cliente"
    )
    estado = django_filters.ChoiceFilter(
        choices=ESTADOS_FACTURA,
        label="Estado"
    )
    fecha_emision = django_filters.DateFromToRangeFilter(
        label="Rango Emisión",
        widget=django_filters.widgets.RangeWidget(attrs={'type': 'date', 'class': 'form-control'})
    )
    numero_factura = django_filters.CharFilter(
        lookup_expr='icontains',
        label="N° Factura"
    )

    class Meta:
        model = Factura
        fields = ['cliente', 'estado', 'fecha_emision', 'numero_factura']