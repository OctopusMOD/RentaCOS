from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView
)
from django_filters.views import FilterView
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import json

from .models import Vehiculo, Marca, ModeloVehiculo, GrupoVehiculo, KilometrajeVehiculo
from .forms import VehiculoForm, MarcaForm, ModeloVehiculoForm, GrupoVehiculoForm, KilometrajeVehiculoForm
from .filters import VehiculoFilter, KilometrajeVehiculoFilter
from django.utils.decorators import method_decorator

# --- API: Obtener kilometraje actual de un vehículo ---
@login_required
def api_kilometraje_actual(request):
    vehiculo_id = request.GET.get('vehiculo_id')
    km = 0
    if vehiculo_id:
        try:
            vehiculo = Vehiculo.objects.get(pk=vehiculo_id)
            km = vehiculo.kilometraje_actual
        except Vehiculo.DoesNotExist:
            pass
    return JsonResponse({'kilometraje': km})

# --- Vehículo CRUD y Dashboard protegidos ---
@method_decorator(login_required, name='dispatch')
class VehiculoListView(FilterView):
    model = Vehiculo
    template_name = "flota/vehiculo_list.html"
    context_object_name = "vehiculos"
    paginate_by = 15
    filterset_class = VehiculoFilter

@method_decorator(login_required, name='dispatch')
class VehiculoDetailView(DetailView):
    model = Vehiculo
    template_name = "flota/vehiculo_detail.html"
    context_object_name = "vehiculo"

@method_decorator(login_required, name='dispatch')
class VehiculoCreateView(CreateView):
    model = Vehiculo
    form_class = VehiculoForm
    template_name = "flota/vehiculo_form.html"
    success_url = reverse_lazy('flota:vehiculo_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        marcas = Marca.objects.prefetch_related('modelos__tipo_carroceria').all()
        context['marcas'] = marcas
        # Serializar modelos por marca para JS seguro
        modelos_por_marca = {}
        for marca in marcas:
            modelos_por_marca[str(marca.id)] = [
                {
                    'id': str(modelo.id),
                    'nombre': modelo.nombre,
                    'carroceria': str(modelo.tipo_carroceria) if modelo.tipo_carroceria else ''
                }
                for modelo in marca.modelos.all()
            ]
        context['modelos_por_marca_json'] = json.dumps(modelos_por_marca)
        return context

@method_decorator(login_required, name='dispatch')
class VehiculoUpdateView(UpdateView):
    model = Vehiculo
    form_class = VehiculoForm
    template_name = "flota/vehiculo_form.html"
    success_url = reverse_lazy('flota:vehiculo_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        marcas = Marca.objects.prefetch_related('modelos__tipo_carroceria').all()
        context['marcas'] = marcas
        # Serializar modelos por marca para JS seguro
        modelos_por_marca = {}
        for marca in marcas:
            modelos_por_marca[str(marca.id)] = [
                {
                    'id': str(modelo.id),
                    'nombre': modelo.nombre,
                    'carroceria': str(modelo.tipo_carroceria) if modelo.tipo_carroceria else ''
                }
                for modelo in marca.modelos.all()
            ]
        context['modelos_por_marca_json'] = json.dumps(modelos_por_marca)
        return context

@method_decorator(login_required, name='dispatch')
class VehiculoDeleteView(DeleteView):
    model = Vehiculo
    template_name = "flota/vehiculo_confirm_delete.html"
    success_url = reverse_lazy('flota:vehiculo_list')

# --- Marca CRUD ---
@method_decorator(login_required, name='dispatch')
class MarcaListView(ListView):
    model = Marca
    template_name = "flota/marca_list.html"
    context_object_name = "marcas"
    paginate_by = 20

@method_decorator(login_required, name='dispatch')
class MarcaCreateView(CreateView):
    model = Marca
    form_class = MarcaForm
    template_name = "flota/marca_form.html"
    success_url = reverse_lazy('flota:marca_list')

@method_decorator(login_required, name='dispatch')
class MarcaUpdateView(UpdateView):
    model = Marca
    form_class = MarcaForm
    template_name = "flota/marca_form.html"
    success_url = reverse_lazy('flota:marca_list')

@method_decorator(login_required, name='dispatch')
class MarcaDeleteView(DeleteView):
    model = Marca
    template_name = "flota/marca_confirm_delete.html"
    success_url = reverse_lazy('flota:marca_list')

# --- ModeloVehiculo CRUD ---
@method_decorator(login_required, name='dispatch')
class ModeloVehiculoListView(ListView):
    model = ModeloVehiculo
    template_name = "flota/modelo_list.html"
    context_object_name = "modelos"
    paginate_by = 20

@method_decorator(login_required, name='dispatch')
class ModeloVehiculoCreateView(CreateView):
    model = ModeloVehiculo
    form_class = ModeloVehiculoForm
    template_name = "flota/modelo_form.html"
    success_url = reverse_lazy('flota:modelo_list')

@method_decorator(login_required, name='dispatch')
class ModeloVehiculoUpdateView(UpdateView):
    model = ModeloVehiculo
    form_class = ModeloVehiculoForm
    template_name = "flota/modelo_form.html"
    success_url = reverse_lazy('flota:modelo_list')

@method_decorator(login_required, name='dispatch')
class ModeloVehiculoDeleteView(DeleteView):
    model = ModeloVehiculo
    template_name = "flota/modelo_confirm_delete.html"
    success_url = reverse_lazy('flota:modelo_list')

# --- GrupoVehiculo CRUD ---
@method_decorator(login_required, name='dispatch')
class GrupoVehiculoListView(ListView):
    model = GrupoVehiculo
    template_name = "flota/grupo_list.html"
    context_object_name = "grupos"
    paginate_by = 20

@method_decorator(login_required, name='dispatch')
class GrupoVehiculoCreateView(CreateView):
    model = GrupoVehiculo
    form_class = GrupoVehiculoForm
    template_name = "flota/grupo_form.html"
    success_url = '/flota/grupos/'

@method_decorator(login_required, name='dispatch')
class GrupoVehiculoUpdateView(UpdateView):
    model = GrupoVehiculo
    form_class = GrupoVehiculoForm
    template_name = "flota/grupo_form.html"
    success_url = '/flota/grupos/'

@method_decorator(login_required, name='dispatch')
class GrupoVehiculoDeleteView(DeleteView):
    model = GrupoVehiculo
    template_name = "flota/grupo_confirm_delete.html"
    success_url = '/flota/grupos/'

# --- Cambiar estado de Vehículo ---
@require_POST
@login_required
def cambiar_estado_vehiculo(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    nuevo_estado_general = request.POST.get('estado_general')
    nuevo_subestado = request.POST.get('subestado')
    actualizado = False
    if nuevo_estado_general in dict(Vehiculo.ESTADO_GENERAL_CHOICES):
        vehiculo.estado_general = nuevo_estado_general
        actualizado = True
    if nuevo_subestado in dict(Vehiculo.SUBESTADO_CHOICES):
        vehiculo.subestado = nuevo_subestado
        actualizado = True
    if actualizado:
        vehiculo.save()
        messages.success(request, f"Estado actualizado a {vehiculo.get_estado_display()}")
    else:
        messages.error(request, "Estado o subestado no válido")
    return redirect(request.META.get("HTTP_REFERER", reverse('flota:vehiculo_list')))

# --- KilometrajeVehiculo CRUD ---
@login_required
def lista_kilometrajes(request):
    kilometrajes = KilometrajeVehiculo.objects.select_related('vehiculo', 'usuario', 'cliente').order_by('-fecha')
    filtro = KilometrajeVehiculoFilter(request.GET, queryset=kilometrajes)

    # Determina si hay filtro por vehículo o por patente
    vehiculo_id = request.GET.get('vehiculo')
    patente = request.GET.get('vehiculo__patente')
    if (vehiculo_id and vehiculo_id.isdigit()) or (patente and patente.strip()):
        # Si hay vehículo filtrado o patente, mostramos todo el historial paginado (ej: 30 por página)
        page_size = 30
        qs = filtro.qs
    else:
        # Sin filtro: mostrar solo los 10 últimos
        page_size = 10
        qs = filtro.qs[:10]

    paginator = Paginator(qs, page_size)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'flota/kilometraje_list.html', {
        'page_obj': page_obj,
        'filtro': filtro,
        'request': request
    })

@login_required
def detalle_kilometraje(request, pk):
    kilometraje = get_object_or_404(KilometrajeVehiculo, pk=pk)
    return render(request, 'flota/kilometraje_detail.html', {'kilometraje': kilometraje})

@login_required
def registrar_kilometraje(request):
    initial = {}
    if request.method == 'GET' and 'vehiculo' in request.GET:
        initial['vehiculo'] = request.GET['vehiculo']
    if request.method == 'POST':
        form = KilometrajeVehiculoForm(request.POST)
        if form.is_valid():
            kilometraje_obj = form.save(commit=False)
            vehiculo = kilometraje_obj.vehiculo
            nuevo_km = kilometraje_obj.kilometraje
            kilometraje_obj.usuario = request.user
            kilometraje_obj.save()
            if nuevo_km > vehiculo.kilometraje_actual:
                vehiculo.kilometraje_actual = nuevo_km
                # --- LÓGICA DE SUBESTADO ---
                if vehiculo.proximo_mantenimiento:
                    diferencia = vehiculo.proximo_mantenimiento - vehiculo.kilometraje_actual
                    if vehiculo.kilometraje_actual >= vehiculo.proximo_mantenimiento:
                        vehiculo.subestado = 'MANTENIMIENTO_ATRASADO'
                    elif diferencia <= 2000:
                        vehiculo.subestado = 'PROX_MANTENIMIENTO'
                    else:
                        vehiculo.subestado = 'NINGUNO'
                    vehiculo.save(update_fields=['kilometraje_actual', 'subestado'])
                else:
                    vehiculo.save(update_fields=['kilometraje_actual'])
            messages.success(request, 'Kilometraje registrado y vehículo actualizado correctamente.')
            return redirect('flota:kilometraje_historial', vehiculo_id=kilometraje_obj.vehiculo.id)
    else:
        form = KilometrajeVehiculoForm(initial=initial)
    return render(request, 'flota/kilometraje_registrar.html', {'form': form})

@login_required
def kilometraje_historial(request, vehiculo_id):
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)
    historial = vehiculo.historial_kilometraje.all().order_by('-fecha')[:10]  # SOLO LOS 10 ÚLTIMOS
    return render(request, 'flota/kilometraje_historial.html', {
        'vehiculo': vehiculo,
        'historial': historial,
    })

@login_required
def kilometraje_historial_completo(request, vehiculo_id):
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)
    historial_qs = vehiculo.historial_kilometraje.all().order_by('-fecha')
    paginator = Paginator(historial_qs, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'flota/kilometraje_historial_completo.html', {
        'vehiculo': vehiculo,
        'page_obj': page_obj,
    })

@login_required
def editar_kilometraje(request, pk):
    kilometraje = get_object_or_404(KilometrajeVehiculo, pk=pk)
    if request.method == 'POST':
        form = KilometrajeVehiculoForm(request.POST, instance=kilometraje)
        if form.is_valid():
            kilometraje_obj = form.save(commit=False)
            vehiculo = kilometraje_obj.vehiculo
            nuevo_km = kilometraje_obj.kilometraje
            kilometraje_obj.save()
            # Actualiza el kilometraje actual si corresponde
            if nuevo_km > vehiculo.kilometraje_actual:
                vehiculo.kilometraje_actual = nuevo_km
                if vehiculo.proximo_mantenimiento:
                    diferencia = vehiculo.proximo_mantenimiento - vehiculo.kilometraje_actual
                    if vehiculo.kilometraje_actual >= vehiculo.proximo_mantenimiento:
                        vehiculo.subestado = 'MANTENIMIENTO_ATRASADO'
                    elif diferencia <= 2000:
                        vehiculo.subestado = 'PROX_MANTENIMIENTO'
                    else:
                        vehiculo.subestado = 'NINGUNO'
                    vehiculo.save(update_fields=['kilometraje_actual', 'subestado'])
                else:
                    vehiculo.save(update_fields=['kilometraje_actual'])
            messages.success(request, 'Kilometraje actualizado correctamente.')
            return redirect('flota:detalle_kilometraje', pk=kilometraje.pk)
    else:
        form = KilometrajeVehiculoForm(instance=kilometraje)
    return render(request, 'flota/kilometraje_form.html', {'form': form, 'editar': True})

@login_required
def eliminar_kilometraje(request, pk):
    kilometraje = get_object_or_404(KilometrajeVehiculo, pk=pk)
    if request.method == 'POST':
        kilometraje.delete()
        messages.success(request, 'Registro de kilometraje eliminado.')
        return redirect('flota:lista_kilometrajes')
    return render(request, 'flota/kilometraje_confirm_delete.html', {'kilometraje': kilometraje})

@login_required
def dashboard_flota(request):
    # KPIs principales
    total_vehiculos = Vehiculo.objects.count()
    vehiculos_disponibles = Vehiculo.objects.filter(estado_general='DISPONIBLE').count()
    vehiculos_arriendo = Vehiculo.objects.filter(estado_general='EN_ARRIENDO').count()
    vehiculos_taller = Vehiculo.objects.filter(estado_general='EN_TALLER').count() if 'EN_TALLER' in dict(Vehiculo.ESTADO_GENERAL_CHOICES) else 0
    vehiculos_prox_mant = Vehiculo.objects.filter(subestado='PROX_MANTENIMIENTO').count()
    vehiculos_mant_atrasado = Vehiculo.objects.filter(subestado='MANTENIMIENTO_ATRASADO').count()

    # Documentos por vencer o vencidos
    hoy = timezone.now().date()
    docs_por_vencer = Vehiculo.objects.filter(
        Q(fecha_vencimiento_soap__gt=hoy, fecha_vencimiento_soap__lte=hoy + timedelta(days=30)) |
        Q(fecha_vencimiento_rev_tecnica__gt=hoy, fecha_vencimiento_rev_tecnica__lte=hoy + timedelta(days=30)) |
        Q(fecha_vencimiento_permiso_circulacion__gt=hoy, fecha_vencimiento_permiso_circulacion__lte=hoy + timedelta(days=30))
    ).distinct().count()
    docs_vencidos = Vehiculo.objects.filter(
        Q(fecha_vencimiento_soap__lt=hoy) |
        Q(fecha_vencimiento_rev_tecnica__lt=hoy) |
        Q(fecha_vencimiento_permiso_circulacion__lt=hoy)
    ).distinct().count()

    # Últimos 5 movimientos de kilometraje
    ultimos_kilometrajes = KilometrajeVehiculo.objects.select_related('vehiculo').order_by('-fecha')[:5]

    # Vehículos con alertas críticas
    alertas_criticas = Vehiculo.objects.filter(
        Q(subestado='MANTENIMIENTO_ATRASADO') |
        Q(subestado='PROX_MANTENIMIENTO') |
        Q(fecha_vencimiento_soap__lt=hoy) |
        Q(fecha_vencimiento_rev_tecnica__lt=hoy) |
        Q(fecha_vencimiento_permiso_circulacion__lt=hoy) |
        Q(fecha_vencimiento_soap__gt=hoy, fecha_vencimiento_soap__lte=hoy+timedelta(days=30)) |
        Q(fecha_vencimiento_rev_tecnica__gt=hoy, fecha_vencimiento_rev_tecnica__lte=hoy+timedelta(days=30)) |
        Q(fecha_vencimiento_permiso_circulacion__gt=hoy, fecha_vencimiento_permiso_circulacion__lte=hoy+timedelta(days=30))
    ).distinct().order_by('subestado', 'fecha_vencimiento_soap')[:10]

    context = {
        'total_vehiculos': total_vehiculos,
        'vehiculos_disponibles': vehiculos_disponibles,
        'vehiculos_arriendo': vehiculos_arriendo,
        'vehiculos_taller': vehiculos_taller,
        'vehiculos_prox_mant': vehiculos_prox_mant,
        'vehiculos_mant_atrasado': vehiculos_mant_atrasado,
        'docs_por_vencer': docs_por_vencer,
        'docs_vencidos': docs_vencidos,
        'ultimos_kilometrajes': ultimos_kilometrajes,
        'alertas_criticas': alertas_criticas,
    }
    return render(request, "flota/dashboard_flota.html", context)