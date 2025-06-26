from django.urls import reverse_lazy
from django.views import generic
from .models import TipoMantenimiento, OrdenMantenimiento, ItemRepuesto, ConsumoRepuesto, Taller
from .forms import (
    TipoMantenimientoForm, OrdenMantenimientoForm,
    ItemRepuestoForm, ConsumoRepuestoForm, TallerForm
)
from django.shortcuts import render, redirect
from .forms import (
    OrdenMantenimientoForm, TrabajoRealizadoFormSet, ConsumoRepuestoFormSet
)

# CRUD Taller
class TallerListView(generic.ListView):
    model = Taller
    template_name = "mantenimiento/taller_list.html"
    context_object_name = "talleres"

class TallerCreateView(generic.CreateView):
    model = Taller
    form_class = TallerForm
    template_name = "mantenimiento/taller_form.html"
    success_url = reverse_lazy("mantenimiento:taller_list")

class TallerUpdateView(generic.UpdateView):
    model = Taller
    form_class = TallerForm
    template_name = "mantenimiento/taller_form.html"
    success_url = reverse_lazy("mantenimiento:taller_list")

# TipoMantenimiento Views
class TipoMantenimientoListView(generic.ListView):
    model = TipoMantenimiento
    template_name = "mantenimiento/tipo_list.html"
    context_object_name = "tipos"

class TipoMantenimientoCreateView(generic.CreateView):
    model = TipoMantenimiento
    form_class = TipoMantenimientoForm
    template_name = "mantenimiento/tipo_form.html"
    success_url = reverse_lazy("mantenimiento:tipo_list")

class TipoMantenimientoUpdateView(generic.UpdateView):
    model = TipoMantenimiento
    form_class = TipoMantenimientoForm
    template_name = "mantenimiento/tipo_form.html"
    success_url = reverse_lazy("mantenimiento:tipo_list")

# ItemRepuesto Views
class ItemRepuestoListView(generic.ListView):
    model = ItemRepuesto
    template_name = "mantenimiento/repuesto_list.html"
    context_object_name = "repuestos"

class ItemRepuestoCreateView(generic.CreateView):
    model = ItemRepuesto
    form_class = ItemRepuestoForm
    template_name = "mantenimiento/repuesto_form.html"
    success_url = reverse_lazy("mantenimiento:repuesto_list")

class ItemRepuestoUpdateView(generic.UpdateView):
    model = ItemRepuesto
    form_class = ItemRepuestoForm
    template_name = "mantenimiento/repuesto_form.html"
    success_url = reverse_lazy("mantenimiento:repuesto_list")

# OrdenMantenimiento Views
class OrdenMantenimientoListView(generic.ListView):
    model = OrdenMantenimiento
    template_name = "mantenimiento/orden_list.html"
    context_object_name = "ordenes"

class OrdenMantenimientoCreateView(generic.CreateView):
    model = OrdenMantenimiento
    form_class = OrdenMantenimientoForm
    template_name = "mantenimiento/orden_form.html"
    success_url = reverse_lazy("mantenimiento:orden_list")

class OrdenMantenimientoDetailView(generic.DetailView):
    model = OrdenMantenimiento
    template_name = "mantenimiento/orden_detail.html"
    context_object_name = "orden"

class OrdenMantenimientoUpdateView(generic.UpdateView):
    model = OrdenMantenimiento
    form_class = OrdenMantenimientoForm
    template_name = "mantenimiento/orden_form.html"
    success_url = reverse_lazy("mantenimiento:orden_list")

def orden_mantenimiento_create(request):
    if request.method == 'POST':
        form = OrdenMantenimientoForm(request.POST)
        trabajos_formset = TrabajoRealizadoFormSet(request.POST, prefix='trabajos')
        repuestos_formset = ConsumoRepuestoFormSet(request.POST, prefix='repuestos')
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
        repuestos_formset = ConsumoRepuestoFormSet(prefix='repuestos')
    return render(request, 'mantenimiento/orden_form.html', {
        'form': form,
        'trabajos_formset': trabajos_formset,
        'repuestos_formset': repuestos_formset
    })

# ConsumoRepuesto Views
class ConsumoRepuestoListView(generic.ListView):
    model = ConsumoRepuesto
    template_name = "mantenimiento/consumo_list.html"
    context_object_name = "consumos"

class ConsumoRepuestoCreateView(generic.CreateView):
    model = ConsumoRepuesto
    form_class = ConsumoRepuestoForm
    template_name = "mantenimiento/consumo_form.html"
    success_url = reverse_lazy("mantenimiento:consumo_list")

class ConsumoRepuestoUpdateView(generic.UpdateView):
    model = ConsumoRepuesto
    form_class = ConsumoRepuestoForm
    template_name = "mantenimiento/consumo_form.html"
    success_url = reverse_lazy("mantenimiento:consumo_list")