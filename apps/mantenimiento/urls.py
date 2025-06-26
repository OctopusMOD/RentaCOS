from django.urls import path
from . import views

app_name = "mantenimiento"

urlpatterns = [
    # Talleres
    path('talleres/', views.TallerListView.as_view(), name='taller_list'),
    path('talleres/nuevo/', views.TallerCreateView.as_view(), name='taller_create'),
    path('talleres/<int:pk>/editar/', views.TallerUpdateView.as_view(), name='taller_update'),

    # Tipos de Mantenimiento
    path('tipos/', views.TipoMantenimientoListView.as_view(), name='tipo_list'),
    path('tipos/nuevo/', views.TipoMantenimientoCreateView.as_view(), name='tipo_create'),
    path('tipos/<int:pk>/editar/', views.TipoMantenimientoUpdateView.as_view(), name='tipo_update'),

    # Repuestos
    path('repuestos/', views.ItemRepuestoListView.as_view(), name='repuesto_list'),
    path('repuestos/nuevo/', views.ItemRepuestoCreateView.as_view(), name='repuesto_create'),
    path('repuestos/<int:pk>/editar/', views.ItemRepuestoUpdateView.as_view(), name='repuesto_update'),

    # Ordenes de Mantenimiento
    path('ordenes/', views.OrdenMantenimientoListView.as_view(), name='orden_list'),
    path('ordenes/nueva/', views.orden_mantenimiento_create, name='orden_create'),  # <--- CORREGIDO AQUÍ
    path('ordenes/<int:pk>/', views.OrdenMantenimientoDetailView.as_view(), name='orden_detail'),
    path('ordenes/<int:pk>/editar/', views.OrdenMantenimientoUpdateView.as_view(), name='orden_update'),

    # Consumos de Repuesto
    path('consumos/', views.ConsumoRepuestoListView.as_view(), name='consumo_list'),
    path('consumos/nuevo/', views.ConsumoRepuestoCreateView.as_view(), name='consumo_create'),
    path('consumos/<int:pk>/editar/', views.ConsumoRepuestoUpdateView.as_view(), name='consumo_update'),
]