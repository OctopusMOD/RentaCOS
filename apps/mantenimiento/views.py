from django.template.loader import get_template
from django.http import HttpResponse
import weasyprint
# Exportar OrdenIngreso a PDF
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

@login_required
def orden_ingreso_exportar_pdf(request, pk):
    orden = get_object_or_404(OrdenIngreso, pk=pk)
    template = get_template("mantenimiento/orden_ingreso_detail.html")
    html = template.render({"orden": orden})
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'filename="OI_{orden.numero_orden}.pdf"'
    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response)
    return response
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views import generic
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy

from .models import (
    TipoMantenimiento, OrdenMantenimiento, Taller,
    OrdenIngreso, TrabajoSolicitado, TrabajoRealizado, RepuestoUtilizado
)
from .forms import (
    TipoMantenimientoForm, OrdenMantenimientoForm,
    TallerForm, OrdenIngresoForm,
    OrdenMantenimientoForm, TrabajoRealizadoFormSet, RepuestoUtilizadoFormSet, TrabajoSolicitadoFormSet
)
from apps.flota.models import Vehiculo
from django.core.exceptions import ValidationError

# --- Utilidad ---
def obtener_kilometraje_actual(vehiculo):
    return vehiculo.kilometraje_actual

# --- AJAX: Info de vehículo ---
@login_required
def vehiculo_info(request):
    vehiculo_id = request.GET.get('vehiculo_id')
    data = {}
    try:
        v = Vehiculo.objects.get(id=vehiculo_id)
        data['patente'] = v.patente
        data['marca'] = v.modelo.marca.nombre
        data['modelo'] = v.modelo.nombre
        data['anio_modelo'] = v.modelo.anio
        data['vin'] = v.vin
        arriendo = getattr(v, "arriendos", None)
        if arriendo is not None:
            arriendo_activo = arriendo.filter(activo=True).first()
            data['cliente'] = arriendo_activo.cliente.nombre if arriendo_activo else None
        else:
            data['cliente'] = None
    except Vehiculo.DoesNotExist:
        data['error'] = "Vehículo no encontrado"
    return JsonResponse(data)

# --- AJAX: Siguiente número de OT ---
@login_required
def next_ot_numero(request):
    last = OrdenMantenimiento.objects.order_by('-id').first()
    next_number = 1 if not last or not last.numero_orden else int(last.numero_orden.split('-')[1]) + 1
    return JsonResponse({'numero_orden': f'OT-{next_number:02d}'})

# --- CRUD Taller ---
class TallerListView(LoginRequiredMixin, generic.ListView):
    model = Taller
    template_name = "mantenimiento/taller_list.html"
    context_object_name = "talleres"


class TallerCreateView(LoginRequiredMixin, generic.CreateView):
    model = Taller
    form_class = TallerForm
    template_name = "mantenimiento/taller_form.html"
    success_url = reverse_lazy("mantenimiento:taller_list")

    def form_valid(self, form):
        form.instance.usuario_creador = self.request.user
        return super().form_valid(form)

class TallerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Taller
    form_class = TallerForm
    template_name = "mantenimiento/taller_form.html"
    success_url = reverse_lazy("mantenimiento:taller_list")

# --- CRUD TipoMantenimiento ---
class TipoMantenimientoListView(LoginRequiredMixin, generic.ListView):
    model = TipoMantenimiento
    template_name = "mantenimiento/tipo_list.html"
    context_object_name = "tipos"

class TipoMantenimientoCreateView(LoginRequiredMixin, generic.CreateView):
    model = TipoMantenimiento
    form_class = TipoMantenimientoForm
    template_name = "mantenimiento/tipo_form.html"
    success_url = reverse_lazy("mantenimiento:tipo_list")

class TipoMantenimientoUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = TipoMantenimiento
    form_class = TipoMantenimientoForm
    template_name = "mantenimiento/tipo_form.html"
    success_url = reverse_lazy("mantenimiento:tipo_list")

# --- CRUD OrdenMantenimiento ---
class OrdenMantenimientoListView(LoginRequiredMixin, generic.ListView):
    model = OrdenMantenimiento
    template_name = "mantenimiento/orden_list.html"
    context_object_name = "ordenes"

class OrdenMantenimientoCreateView(LoginRequiredMixin, generic.CreateView):
    model = OrdenMantenimiento
    form_class = OrdenMantenimientoForm
    template_name = "mantenimiento/orden_form.html"
    success_url = reverse_lazy("mantenimiento:orden_list")

class OrdenMantenimientoDetailView(LoginRequiredMixin, generic.DetailView):
    model = OrdenMantenimiento
    template_name = "mantenimiento/orden_detail.html"
    context_object_name = "orden"

class OrdenMantenimientoUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = OrdenMantenimiento
    form_class = OrdenMantenimientoForm
    template_name = "mantenimiento/orden_form.html"
    success_url = reverse_lazy("mantenimiento:orden_list")

@login_required
def orden_mantenimiento_create(request):
    if request.method == 'POST':
        form = OrdenMantenimientoForm(request.POST)
        trabajos_formset = TrabajoRealizadoFormSet(request.POST, prefix='trabajos')
        repuestos_formset = RepuestoUtilizadoFormSet(request.POST, prefix='repuestos')
        if form.is_valid() and trabajos_formset.is_valid() and repuestos_formset.is_valid():
            orden = form.save()
            trabajos_formset.instance = orden
            repuestos_formset.instance = orden
            trabajos_formset.save()
            repuestos_formset.save()
            return redirect('mantenimiento:orden_list')
    else:
        form = OrdenMantenimientoForm()
        trabajos_formset = TrabajoRealizadoFormSet(prefix='trabajos')
        repuestos_formset = RepuestoUtilizadoFormSet(prefix='repuestos')
    return render(request, 'mantenimiento/orden_form.html', {
        'form': form,
        'trabajos_formset': trabajos_formset,
        'repuestos_formset': repuestos_formset
    })

# --- CRUD OrdenIngreso ---
class OrdenIngresoListView(LoginRequiredMixin, generic.ListView):
    model = OrdenIngreso
    template_name = "mantenimiento/orden_ingreso_list.html"
    context_object_name = "ordenes"
    ordering = ['-fecha_ingreso']

class OrdenIngresoDetailView(LoginRequiredMixin, generic.DetailView):
    model = OrdenIngreso
    template_name = "mantenimiento/orden_ingreso_detail.html"
    context_object_name = "orden"

@login_required
def crear_orden_ingreso(request):
    alerta_mantenimiento = None
    if request.method == 'POST':
        form = OrdenIngresoForm(request.POST)
        formset = TrabajoSolicitadoFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            orden = form.save()
            trabajos = formset.save(commit=False)
            for trabajo in trabajos:
                trabajo.orden_ingreso = orden
                trabajo.save()
            return redirect('mantenimiento:orden_ingreso_detalle', pk=orden.pk)
    else:
        form = OrdenIngresoForm()
        formset = TrabajoSolicitadoFormSet()
    # Advertencia: último mantenimiento correctivo
    vehiculo = None
    if 'vehiculo' in form.initial:
        vehiculo = form.initial.get('vehiculo')
    elif hasattr(form, 'instance') and form.instance and getattr(form.instance, 'vehiculo', None):
        vehiculo = form.instance.vehiculo
    if vehiculo:
        ult = OrdenMantenimiento.objects.filter(
            vehiculo=vehiculo, 
            tipo__nombre__icontains='Correctivo'
        ).order_by('-fecha_ingreso').first()
        if ult:
            alerta_mantenimiento = f'¡Advertencia! El último mantenimiento correctivo de este vehículo fue el {ult.fecha_ingreso}'
    return render(request, 'mantenimiento/orden_ingreso_form.html', {
        'form': form,
        'formset': formset,
        'alerta_mantenimiento': alerta_mantenimiento
    })

# --- Cancelar OrdenIngreso ---
@login_required
def cancelar_orden_ingreso(request, pk):
    orden = get_object_or_404(OrdenIngreso, pk=pk)
    orden.estado = 'CANCELADA'
    orden.save()
    return redirect('mantenimiento:orden_ingreso_detail', pk=pk)

# --- Convertir OI en OT ---
@login_required
def convertir_oi_en_ot(request, pk):
    oi = get_object_or_404(OrdenIngreso, pk=pk)
    if oi.estado == "CANCELADA":
        return redirect('mantenimiento:orden_ingreso_detail', pk=pk)
    if request.method == 'POST':
        ot = OrdenMantenimiento.objects.create(
            vehiculo=oi.vehiculo,
            taller=oi.taller,
            tipo=oi.tipo_mantenimiento,
            kilometraje_ingreso_mantenimiento=oi.kilometraje_actual or oi.vehiculo.kilometraje_actual,
            descripcion_problema=f"Convertido desde {oi.numero_orden}",
        )
        return redirect('mantenimiento:orden_update', pk=ot.pk)
    return redirect('mantenimiento:orden_ingreso_detail', pk=pk)

# --- Crear Orden Mantenimiento (alternativo) ---
@login_required
def crear_orden_mantenimiento(request):
    if request.method == 'POST':
        form = OrdenMantenimientoForm(request.POST)
        trabajos_formset = TrabajoRealizadoFormSet(request.POST, prefix='trabajos')
        repuestos_formset = RepuestoUtilizadoFormSet(request.POST, prefix='repuestos')
        if form.is_valid() and trabajos_formset.is_valid() and repuestos_formset.is_valid():
            orden = form.save()
            trabajos_formset.instance = orden
            repuestos_formset.instance = orden
            trabajos_formset.save()
            repuestos_formset.save()
            return redirect('mantenimiento:orden_list')
    else:
        form = OrdenMantenimientoForm()
        trabajos_formset = TrabajoRealizadoFormSet(prefix='trabajos')
        repuestos_formset = RepuestoUtilizadoFormSet(prefix='repuestos')
    return render(request, 'mantenimiento/orden_form.html', {
        'form': form,
        'trabajos_formset': trabajos_formset,
        'repuestos_formset': repuestos_formset
    })

# --- Dashboard de Mantenimiento ---
@method_decorator(login_required, name='dispatch')
class MantenimientoDashboardView(TemplateView):
    template_name = "mantenimiento/dashboard_mantenimiento.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_ordenes"] = OrdenMantenimiento.objects.count()
        context["ordenes_abiertas"] = OrdenMantenimiento.objects.filter(estado="ABIERTA").count()
        context["ordenes_cerradas"] = OrdenMantenimiento.objects.filter(estado="CERRADA").count()
        # Puedes agregar más KPIs aquí
        return context