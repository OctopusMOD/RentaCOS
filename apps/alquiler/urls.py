from django.urls import path
from . import views
from .views import (
    FacturaListView, FacturaCreateView, FacturaUpdateView, FacturaDeleteView,
    ReservaListView, ContratoListView, AlquilerDashboardView,
)

app_name = 'alquiler'

urlpatterns = [
    # API y utilidades
    path('contratos/<int:pk>/extender-inline/', views.contrato_extender_inline, name='contrato_extender_inline'),
    path('api/clientes/<int:cliente_id>/datos-contacto/', views.api_cliente_datos_contacto, name="api_cliente_datos_contacto"),
    path('api/vehiculo/<int:vehiculo_id>/', views.api_vehiculo_detalle, name='api_vehiculo_detalle'),
    path('api/datos_contrato/<int:contrato_id>/', views.api_datos_contrato, name='api_datos_contrato'),
    path('dashboard/', AlquilerDashboardView.as_view(), name='dashboard'),

    # Clientes
    path('clientes/', views.cliente_list, name='cliente_list'),
    path('clientes/nuevo/', views.cliente_create, name='cliente_create'),
    path('clientes/<int:pk>/', views.cliente_detail, name='cliente_detail'),
    path('clientes/<int:pk>/editar/', views.cliente_update, name='cliente_update'),
    path('clientes/<int:pk>/toggle_status/', views.cliente_toggle_status, name='cliente_toggle_status'),

    # Reservas
    path('reservas/', ReservaListView.as_view(), name='reserva_list'),
    path('reservas/nueva/', views.reserva_create, name='reserva_create'),
    path('reservas/<int:pk>/', views.reserva_detail, name='reserva_detail'),
    path('reservas/<int:pk>/editar/', views.reserva_update, name='reserva_update'),
    path('reservas/<int:pk>/eliminar/', views.reserva_delete, name='reserva_delete'),
    path('reservas/<int:pk>/cambiar_estado/', views.reserva_change_status, name='reserva_change_status'),
    path('reservas/<int:pk>/confirmar/', views.reserva_confirmar, name='reserva_confirmar'),
    path('reservas/<int:pk>/cancelar/', views.reserva_cancelar, name='reserva_cancelar'),

    # Contratos
    path('contratos/', ContratoListView.as_view(), name='contrato_list'),
    path('contratos/nuevo/', views.contrato_create, name='contrato_create'),
    path('contratos/<int:pk>/', views.contrato_detail, name='contrato_detail'),
    path('contratos/<int:pk>/editar/', views.contrato_update, name='contrato_update'),
    path('contratos/<int:pk>/eliminar/', views.contrato_delete, name='contrato_delete'),
    path('contratos/<int:pk>/add-extra/', views.contrato_add_extra, name='contrato_add_extra'),
    path('contratos/<int:pk>/firmar/', views.contrato_firmar, name='contrato_firmar'),
    path('contratos/<int:pk>/terminar/', views.contrato_terminar, name='contrato_terminar'),
    path('contrato/<int:pk>/pdf/', views.contrato_pdf, name='contrato_pdf'),
    path('contratos/<int:pk>/cancelar/', views.contrato_cancelar, name='contrato_cancelar'),

    # Facturas (CRUD)
    path('facturas/', FacturaListView.as_view(), name='factura_list'),
    path('facturas/nueva/', FacturaCreateView.as_view(), name='factura_create'),
    path('facturas/<int:pk>/editar/', FacturaUpdateView.as_view(), name='factura_update'),
    path('facturas/<int:pk>/eliminar/', FacturaDeleteView.as_view(), name='factura_delete'),

    # Factura - vistas adicionales y flujo custom
    path('factura/<int:pk>/', views.factura_detail, name='factura_detail'),
    path('factura/nueva/', views.factura_create, name='factura_create'),
    path('contrato/<int:contrato_pk>/factura/nueva/', views.factura_create_from_contrato, name='factura_create_from_contrato'),
    path('factura/<int:pk>/anular/', views.factura_anular, name='factura_anular'),

    # Notas
    path('factura/<int:factura_pk>/nota/nueva/', views.nota_create, name='nota_create'),
    path('nota/<int:pk>/', views.nota_detail, name='nota_detail'),
]