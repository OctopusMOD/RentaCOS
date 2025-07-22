from django.urls import path
from django.shortcuts import redirect
from .views import MantenimientoDashboardView
from . import views

app_name = "mantenimiento"

urlpatterns = [
    # Redirección a dashboard
    path('', lambda request: redirect('mantenimiento:dashboard_mantenimiento', permanent=False)),

    # Dashboard
    path('dashboard/', MantenimientoDashboardView.as_view(), name='dashboard_mantenimiento'),

    # Talleres
    path('talleres/', views.TallerListView.as_view(), name='taller_list'),
    path('talleres/nuevo/', views.TallerCreateView.as_view(), name='taller_create'),
    path('talleres/<int:pk>/editar/', views.TallerUpdateView.as_view(), name='taller_update'),

    # Tipos de Mantenimiento
    path('tipos/', views.TipoMantenimientoListView.as_view(), name='tipo_list'),
    path('tipos/nuevo/', views.TipoMantenimientoCreateView.as_view(), name='tipo_create'),
    path('tipos/<int:pk>/editar/', views.TipoMantenimientoUpdateView.as_view(), name='tipo_update'),

    # Órdenes de Mantenimiento
    path('ordenes/', views.OrdenMantenimientoListView.as_view(), name='orden_list'),
    path('ordenes/nueva/', views.orden_mantenimiento_create, name='orden_create'),
    path('ordenes/<int:pk>/', views.OrdenMantenimientoDetailView.as_view(), name='orden_detail'),
    path('ordenes/<int:pk>/editar/', views.OrdenMantenimientoUpdateView.as_view(), name='orden_update'),

    # Órdenes de Ingreso
    path('orden-ingreso/', views.OrdenIngresoListView.as_view(), name='orden_ingreso_list'),
    path('orden-ingreso/nueva/', views.crear_orden_ingreso, name='orden_ingreso_nueva'),
    path('orden-ingreso/<int:pk>/', views.OrdenIngresoDetailView.as_view(), name='orden_ingreso_detalle'),
    path('orden-ingreso/<int:pk>/pdf/', views.orden_ingreso_exportar_pdf, name='orden_ingreso_pdf'),
    path('orden-ingreso/<int:pk>/convertir_ot/', views.convertir_oi_en_ot, name='orden_ingreso_convertir_ot'),
    path('orden-ingreso/<int:pk>/cancelar/', views.cancelar_orden_ingreso, name='orden_ingreso_cancelar'),

    # AJAX utilidades
    path('vehiculo-info/', views.vehiculo_info, name='vehiculo_info'),
    path('next_ot_numero/', views.next_ot_numero, name='next_ot_numero'),
]