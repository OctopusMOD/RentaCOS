from django.urls import path
from . import views
from .views import (
    registrar_kilometraje,
    lista_kilometrajes,
    detalle_kilometraje,
    editar_kilometraje,
    eliminar_kilometraje,
)

app_name = "flota"

urlpatterns = [
    # Vehículos
    path('vehiculos/', views.VehiculoListView.as_view(), name='vehiculo_list'),
    path('vehiculos/nuevo/', views.VehiculoCreateView.as_view(), name='vehiculo_create'),
    path('vehiculos/<int:pk>/', views.VehiculoDetailView.as_view(), name='vehiculo_detail'),
    path('vehiculos/<int:pk>/editar/', views.VehiculoUpdateView.as_view(), name='vehiculo_update'),
    path('vehiculos/<int:pk>/eliminar/', views.VehiculoDeleteView.as_view(), name='vehiculo_delete'),
    path('vehiculos/<int:pk>/cambiar-estado/', views.cambiar_estado_vehiculo, name='cambiar_estado_vehiculo'),

    # Grupos
    path('grupos/', views.GrupoVehiculoListView.as_view(), name='grupo_list'),
    path('grupos/nuevo/', views.GrupoVehiculoCreateView.as_view(), name='grupo_create'),
    path('grupos/<int:pk>/editar/', views.GrupoVehiculoUpdateView.as_view(), name='grupo_update'),
    path('grupos/<int:pk>/eliminar/', views.GrupoVehiculoDeleteView.as_view(), name='grupo_delete'),

    # Marcas
    path('marcas/', views.MarcaListView.as_view(), name='marca_list'),
    path('marcas/nueva/', views.MarcaCreateView.as_view(), name='marca_create'),
    path('marcas/<int:pk>/editar/', views.MarcaUpdateView.as_view(), name='marca_update'),
    path('marcas/<int:pk>/eliminar/', views.MarcaDeleteView.as_view(), name='marca_delete'),

    # Modelos
    path('modelos/', views.ModeloVehiculoListView.as_view(), name='modelo_list'),
    path('modelos/nuevo/', views.ModeloVehiculoCreateView.as_view(), name='modelo_create'),
    path('modelos/<int:pk>/editar/', views.ModeloVehiculoUpdateView.as_view(), name='modelo_update'),
    path('modelos/<int:pk>/eliminar/', views.ModeloVehiculoDeleteView.as_view(), name='modelo_delete'),

    # Kilometrajes global CRUD
    path('kilometrajes/', lista_kilometrajes, name='lista_kilometrajes'),
    path('kilometrajes/registrar/', registrar_kilometraje, name='kilometraje_registrar'),
    path('kilometrajes/<int:pk>/', detalle_kilometraje, name='detalle_kilometraje'),
    path('kilometrajes/<int:pk>/editar/', editar_kilometraje, name='editar_kilometraje'),
    path('kilometrajes/<int:pk>/eliminar/', eliminar_kilometraje, name='eliminar_kilometraje'),

    # Kilometraje por vehículo (historial y registro rápido)
    path('kilometraje/registrar/', registrar_kilometraje, name='kilometraje_registrar'),  # acceso directo, puedes dejarlo o quitarlo si prefieres solo el de arriba
    path('kilometraje/historial/<int:vehiculo_id>/', views.kilometraje_historial, name='kilometraje_historial'),
    path('kilometraje/historial_completo/<int:vehiculo_id>/', views.kilometraje_historial_completo, name='kilometraje_historial_completo'),

    # Dashboard Flota
    path('dashboard/', views.dashboard_flota, name='dashboard_flota'),

    # API simple: kilometraje actual
    path('api/kilometraje_actual/', views.api_kilometraje_actual, name='api_kilometraje_actual'),
]