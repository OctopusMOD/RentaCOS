from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from decimal import Decimal  # <--- IMPORTANTE para cálculos con Decimal
from .models import Cliente, Reserva, Contrato, Factura, Nota  # Vehiculo removido temporalmente
from .forms import ClienteForm, ReservaForm, ContratoForm, FacturaForm, NotaForm
from .filters import ReservaFilter, ContratoFilter, FacturaFilter
from django.utils.decorators import method_decorator
from django_filters.views import FilterView

# DASHBOARD
@login_required
def dashboard(request):
    total_clientes = Cliente.objects.filter(activo=True).count()
    total_reservas = Reserva.objects.all().count()
    reservas_activas = Reserva.objects.filter(
        estado__in=['PENDIENTE', 'CONFIRMADA', 'EN_PROGRESO']
    ).count()
    reservas_por_estado = Reserva.objects.values('estado').annotate(
        total=Count('id')
    ).order_by('estado')
    proximas_reservas = Reserva.objects.filter(
        fecha_inicio__gte=timezone.now()
    ).order_by('fecha_inicio')[:5]
    facturas_pendientes = Factura.objects.filter(
        estado='PENDIENTE',
        fecha_vencimiento__gte=timezone.now()
    ).order_by('fecha_vencimiento')[:5]
    context = {
        'total_clientes': total_clientes,
        'total_reservas': total_reservas,
        'reservas_activas': reservas_activas,
        'reservas_por_estado': reservas_por_estado,
        'proximas_reservas': proximas_reservas,
        'facturas_pendientes': facturas_pendientes,
    }
    return render(request, 'alquiler/dashboard.html', context)

# CRUD CLIENTES
@login_required
def cliente_list(request):
    queryset = Cliente.objects.all()
    tipo = request.GET.get('tipo')
    if tipo:
        queryset = queryset.filter(tipo_cliente=tipo)
    estado = request.GET.get('estado')
    if estado:
        queryset = queryset.filter(activo=(estado == 'activo'))
    region = request.GET.get('region')
    if region:
        queryset = queryset.filter(region=region)
    q = request.GET.get('q')
    if q:
        queryset = queryset.filter(
            Q(razon_social__icontains=q) |
            Q(nombre_comercial__icontains=q) |
            Q(rut_empresa__icontains=q) |
            Q(nombre_contacto__icontains=q) |
            Q(apellidos_contacto__icontains=q) |
            Q(email_empresa__icontains=q) |
            Q(email_contacto__icontains=q)
        )
    sort = request.GET.get('sort', '-fecha_registro')
    queryset = queryset.order_by(sort)
    paginator = Paginator(queryset, 10)
    page = request.GET.get('page')
    try:
        clientes = paginator.page(page)
    except PageNotAnInteger:
        clientes = paginator.page(1)
    except EmptyPage:
        clientes = paginator.page(paginator.num_pages)
    regiones = Cliente.objects.values_list('region', flat=True).distinct()
    context = {
        'clientes': clientes,
        'tipos_cliente': Cliente.TIPO_CLIENTE_CHOICES,
        'regiones': regiones,
        'selected_tipo': tipo,
        'selected_estado': estado,
        'selected_region': region,
        'query': q,
        'sort': sort
    }
    return render(request, 'alquiler/cliente_list.html', context)

@login_required
def cliente_create(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            tipo_cliente = "empresarial" if cliente.tipo_cliente == "EMPRESA" else "particular"
            messages.success(request, f'Cliente {tipo_cliente} creado exitosamente.')
            return redirect('alquiler:cliente_detail', pk=cliente.pk)
        else:
            print("Errores del formulario al crear cliente:")
            print(form.errors)
    else:
        form = ClienteForm()
    return render(request, 'alquiler/cliente_form.html', {
        'form': form,
        'title': 'Nuevo Cliente'
    })

@login_required
def cliente_detail(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    reservas = cliente.reservas.all().order_by('-fecha_reserva')
    total_reservas = reservas.count()
    reservas_activas = reservas.filter(
        estado__in=['PENDIENTE', 'CONFIRMADA', 'EN_PROGRESO']
    ).count()
    monto_total = reservas.aggregate(
        total=Sum('monto_total')
    )['total'] or 0
    # CORREGIDO: relación correcta hacia facturas
    facturas_pendientes = Factura.objects.filter(
        contrato__reserva__cliente=cliente,
        estado='PENDIENTE'
    ).order_by('fecha_vencimiento')
    context = {
        'cliente': cliente,
        'reservas': reservas[:5],
        'total_reservas': total_reservas,
        'reservas_activas': reservas_activas,
        'monto_total': monto_total,
        'facturas_pendientes': facturas_pendientes
    }
    return render(request, 'alquiler/cliente_detail.html', context)

@login_required
def cliente_update(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, 'Cliente actualizado exitosamente.')
            return redirect('alquiler:cliente_detail', pk=pk)
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'alquiler/cliente_form.html', {
        'form': form,
        'cliente': cliente,
        'title': 'Editar Cliente'
    })

@login_required
@require_http_methods(["POST"])
def cliente_toggle_status(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    cliente.activo = not cliente.activo
    cliente.save()
    status = 'activado' if cliente.activo else 'desactivado'
    messages.success(request, f'Cliente {status} exitosamente.')
    return JsonResponse({
        'status': 'success',
        'active': cliente.activo
    })

# CRUD RESERVAS
@method_decorator(login_required, name='dispatch')
class ReservaListView(FilterView):
    model = Reserva
    template_name = 'alquiler/reserva_list.html'
    context_object_name = 'reservas'
    filterset_class = ReservaFilter
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().select_related('cliente').order_by('-fecha_reserva')

@login_required
def reserva_create(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            # reserva.monto_total = reserva.vehiculo.tarifa_diaria * max(1, dias)
            reserva.monto_total = 0  # O el valor que desees, o pide ese valor en el formulario
            reserva.save()
            messages.success(request, 'Reserva creada exitosamente.')
            return redirect('alquiler:reserva_detail', pk=reserva.pk)
    else:
        initial = {}
        cliente_id = request.GET.get('cliente')
        if cliente_id:
            initial['cliente'] = cliente_id
        form = ReservaForm(initial=initial)
    return render(request, 'alquiler/reserva_form.html', {
        'form': form,
        'title': 'Nueva Reserva'
    })

@login_required
def reserva_detail(request, pk):
    reserva = get_object_or_404(
        Reserva.objects.select_related('cliente'),
        pk=pk
    )
    tiene_contrato = hasattr(reserva, 'contrato')
    tiene_factura = hasattr(reserva, 'factura')
    dias_totales = max(1, (reserva.fecha_fin - reserva.fecha_inicio).days)
    context = {
        'reserva': reserva,
        'tiene_contrato': tiene_contrato,
        'tiene_factura': tiene_factura,
        'dias_totales': dias_totales
    }
    return render(request, 'alquiler/reserva_detail.html', context)

@login_required
def reserva_update(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if not reserva.puede_editar():
        messages.error(request, "Solo puedes editar reservas pendientes.")
        return redirect('alquiler:reserva_detail', pk=pk)
    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            reserva = form.save(commit=False)
            # reserva.monto_total = reserva.vehiculo.tarifa_diaria * max(1, dias)
            reserva.monto_total = 0  # O el valor que desees, o pide ese valor en el formulario
            reserva.save()
            messages.success(request, 'Reserva actualizada exitosamente.')
            return redirect('alquiler:reserva_detail', pk=pk)
    else:
        form = ReservaForm(instance=reserva)
    return render(request, 'alquiler/reserva_form.html', {
        'form': form,
        'reserva': reserva,
        'title': 'Editar Reserva'
    })

@login_required
def reserva_delete(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if not reserva.puede_eliminar():
        messages.error(request, "Solo puedes eliminar reservas pendientes y sin contrato.")
        return redirect('alquiler:reserva_detail', pk=pk)
    if request.method == 'POST':
        reserva.delete()
        messages.success(request, "La reserva fue eliminada correctamente.")
        return redirect('alquiler:reserva_list')
    return render(request, 'alquiler/reserva_confirm_delete.html', {'reserva': reserva})

@login_required
@require_http_methods(["POST"])
def reserva_change_status(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    nuevo_estado = request.POST.get('estado')
    if nuevo_estado in dict(Reserva.ESTADO_CHOICES):
        reserva.estado = nuevo_estado
        reserva.save()
        messages.success(request, f'Estado de la reserva actualizado a {reserva.get_estado_display()}.')
    else:
        messages.error(request, 'Estado no válido.')
    return JsonResponse({
        'status': 'success',
        'nuevo_estado': reserva.get_estado_display()
    })

@login_required
def reserva_confirmar(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if not reserva.puede_confirmar():
        messages.warning(request, "Solo puedes confirmar reservas pendientes.")
        return redirect('alquiler:reserva_detail', pk=pk)
    reserva.estado = 'CONFIRMADA'
    reserva.save()
    messages.success(request, 'Reserva confirmada exitosamente.')
    return redirect('alquiler:reserva_detail', pk=pk)

@login_required
def reserva_cancelar(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if not reserva.puede_cancelar():
        messages.warning(request, "Solo puedes cancelar reservas pendientes o confirmadas.")
        return redirect('alquiler:reserva_detail', pk=pk)
    reserva.estado = 'CANCELADA'
    reserva.save()
    messages.success(request, 'Reserva cancelada exitosamente.')
    return redirect('alquiler:reserva_detail', pk=pk)

# CRUD CONTRATOS
@method_decorator(login_required, name='dispatch')
class ContratoListView(FilterView):
    model = Contrato
    template_name = 'alquiler/contrato_list.html'
    context_object_name = 'contratos'
    filterset_class = ContratoFilter
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().select_related('reserva__cliente').order_by('-fecha_firma')

@login_required
def contrato_create(request):
    reserva_id = request.GET.get('reserva')
    initial = {}
    reserva_obj = None
    if reserva_id:
        try:
            reserva_obj = Reserva.objects.select_related('cliente').get(pk=reserva_id)
            # Validar SOLO aquí: debe estar CONFIRMADA y sin contrato
            if reserva_obj.estado != 'CONFIRMADA' or hasattr(reserva_obj, 'contrato'):
                messages.error(request, "Solo puedes generar contrato para reservas confirmadas y sin contrato asociado.")
                return redirect('alquiler:reserva_detail', pk=reserva_id)
            initial['reserva'] = reserva_obj
            initial['cliente'] = reserva_obj.cliente
        except Reserva.DoesNotExist:
            messages.error(request, "Reserva no encontrada.")
            return redirect('alquiler:reserva_list')

    if request.method == 'POST':
        # Usar reserva_obj si vino por GET, sino tomar del form
        reserva_from_form = reserva_obj or None
        form = ContratoForm(request.POST, request.FILES, initial=initial)
        if form.is_valid():
            contrato = form.save(commit=False)
            reserva_asoc = reserva_from_form or contrato.reserva
            # Validar SOLO aquí, antes de guardar (para evitar error de estado cambiado)
            if reserva_asoc.estado != 'CONFIRMADA' or hasattr(reserva_asoc, 'contrato'):
                messages.error(request, "Solo puedes generar contrato para reservas confirmadas y sin contrato.")
                return redirect('alquiler:reserva_detail', pk=reserva_asoc.pk)
            # Numeración
            año_actual = timezone.now().year
            ultimo_contrato = Contrato.objects.filter(
                numero_contrato__startswith=f'CONT-{año_actual}'
            ).order_by('-numero_contrato').first()
            if ultimo_contrato:
                try:
                    ultimo_numero = int(ultimo_contrato.numero_contrato.split('-')[-1])
                except Exception:
                    ultimo_numero = 0
                nuevo_numero = ultimo_numero + 1
            else:
                nuevo_numero = 1
            contrato.numero_contrato = f'CONT-{año_actual}-{nuevo_numero:04d}'
            if reserva_asoc:
                contrato.reserva = reserva_asoc
                contrato.cliente = reserva_asoc.cliente
            contrato.save()
            # SOLO AHORA actualizar la reserva
            if contrato.reserva:
                contrato.reserva.contrato = contrato
                contrato.reserva.estado = 'COMPLETADA'
                contrato.reserva.save()
            messages.success(request, "Contrato creado exitosamente.")
            return redirect('alquiler:contrato_detail', pk=contrato.pk)
    else:
        form = ContratoForm(initial=initial)
        if reserva_obj:
            form.fields['reserva'].widget.attrs['readonly'] = True
            form.fields['cliente'].widget.attrs['readonly'] = True

    return render(request, 'alquiler/contrato_form.html', {
        'form': form,
        'title': 'Nuevo Contrato',
        'reserva_preseleccionada': reserva_obj is not None,
        'reserva_obj': reserva_obj
    })

@login_required
def contrato_detail(request, pk):
    contrato = get_object_or_404(
        Contrato.objects.select_related('reserva__cliente'),
        pk=pk
    )
    context = {
        'contrato': contrato,
    }
    return render(request, 'alquiler/contrato_detail.html', context)

@login_required
def contrato_update(request, pk):
    contrato = get_object_or_404(Contrato, pk=pk)
    if request.method == 'POST':
        form = ContratoForm(request.POST, request.FILES, instance=contrato)
        if form.is_valid():
            contrato = form.save(commit=False)
            reserva_asociada = contrato.reserva
            if reserva_asociada and reserva_asociada.estado != 'CONFIRMADA':
                messages.error(request, "Solo puedes asociar contratos a reservas en estado CONFIRMADA.")
                return redirect('alquiler:contrato_update', pk=pk)
            contrato.save()
            if reserva_asociada:
                reserva_asociada.contrato = contrato
                reserva_asociada.estado = 'COMPLETADA'
                reserva_asociada.save()
            messages.success(request, 'Contrato actualizado exitosamente.')
            return redirect('alquiler:contrato_detail', pk=pk)
    else:
        form = ContratoForm(instance=contrato)
    return render(request, 'alquiler/contrato_form.html', {
        'form': form,
        'contrato': contrato,
        'title': 'Editar Contrato'
    })

@login_required
def contrato_delete(request, pk):
    contrato = get_object_or_404(Contrato, pk=pk)
    if contrato.estado != 'BORRADOR':
        messages.error(request, "Sólo puedes eliminar contratos en estado BORRADOR.")
        return redirect('alquiler:contrato_detail', pk=pk)
    if request.method == 'POST':
        contrato.delete()
        messages.success(request, "Contrato eliminado correctamente.")
        return redirect('alquiler:contrato_list')
    return render(request, 'alquiler/contrato_confirm_delete.html', {
        'contrato': contrato
    })

# CRUD FACTURAS
@method_decorator(login_required, name='dispatch')
class FacturaListView(FilterView):
    model = Factura
    template_name = 'alquiler/factura_list.html'
    context_object_name = 'facturas'
    filterset_class = FacturaFilter
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().select_related('contrato__reserva__cliente').order_by('-fecha_emision')

@login_required
def factura_create(request):
    contrato_id = request.GET.get('contrato')
    initial = {}

    if contrato_id:
        contrato = get_object_or_404(Contrato, pk=contrato_id)
        cliente = contrato.cliente
        # Ajusta los campos según tu modelo de Contrato y Cliente
        initial = {
            "contrato": contrato,
            "rut_receptor": getattr(cliente, "rut_empresa", "") or getattr(cliente, "numero_documento", ""),
            "razon_social_receptor": getattr(cliente, "razon_social", ""),
            "giro_receptor": getattr(cliente, "giro", ""),
            "direccion_receptor": getattr(cliente, "direccion", ""),
            "subtotal": getattr(contrato, "monto_total", 0) or 0,
        }

    if request.method == "POST":
        form = FacturaForm(request.POST)
        if form.is_valid():
            factura = form.save()
            messages.success(request, "Factura creada correctamente.")
            return redirect("alquiler:factura_detail", pk=factura.pk)
    else:
        form = FacturaForm(initial=initial)

    return render(request, "alquiler/factura_form.html", {"form": form})

@login_required
def factura_detail(request, pk):
    factura = get_object_or_404(
        Factura.objects.select_related('contrato'),  # <--- SOLO 'contrato'
        pk=pk
    )
    dias_vencimiento = None
    if factura.estado == 'PENDIENTE':
        dias_vencimiento = (factura.fecha_vencimiento - timezone.now().date()).days
    context = {
        'factura': factura,
        'dias_vencimiento': dias_vencimiento
    }
    return render(request, 'alquiler/factura_detail.html', context)

@login_required
@require_http_methods(["POST"])
def factura_mark_as_paid(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    if factura.estado == 'PENDIENTE':
        factura.estado = 'PAGADA'
        factura.save()
        messages.success(request, 'Factura marcada como pagada exitosamente.')
    else:
        messages.error(request, 'La factura no está en estado pendiente.')
    return JsonResponse({
        'status': 'success',
        'nuevo_estado': factura.get_estado_display()
    })

class FacturaCreateView(CreateView):
    model = Factura
    form_class = FacturaForm
    template_name = 'alquiler/factura_form.html'
    success_url = reverse_lazy('alquiler:factura_list')

class FacturaUpdateView(UpdateView):
    model = Factura
    form_class = FacturaForm
    template_name = 'alquiler/factura_form.html'
    success_url = reverse_lazy('alquiler:factura_list')

class FacturaDeleteView(DeleteView):
    model = Factura
    template_name = 'alquiler/factura_confirm_delete.html'
    success_url = reverse_lazy('alquiler:factura_list')

@login_required
def contrato_pdf(request, pk):
    contrato = get_object_or_404(Contrato, pk=pk)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="contrato_{contrato.pk}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Encabezado
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 80, "CONTRATO DE ARRENDAMIENTO")

    # Datos del contrato y del cliente
    p.setFont("Helvetica", 12)
    y = height - 120
    p.drawString(50, y, f"Contrato N°: {contrato.pk}")
    y -= 25
    if contrato.reserva and contrato.reserva.cliente:
        p.drawString(50, y, f"Cliente: {getattr(contrato.reserva.cliente, 'nombre_completo', str(contrato.reserva.cliente))}")
        y -= 20
        p.drawString(50, y, f"Documento: {getattr(contrato.reserva.cliente, 'documento', '')}")
        y -= 20
    if contrato.reserva:
        p.drawString(50, y, f"Reserva desde: {contrato.reserva.fecha_inicio} hasta: {contrato.reserva.fecha_fin}")
        y -= 20
    p.drawString(50, y, f"Fecha de contrato: {getattr(contrato, 'fecha', '')}")
    y -= 30

    # Términos (ejemplo)
    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, y, "Términos del contrato:")
    y -= 20
    p.setFont("Helvetica", 12)
    p.drawString(60, y, getattr(contrato, 'terminos', "Términos y condiciones generales..."))

    # Pie de página
    p.setFont("Helvetica", 10)
    p.drawString(50, 40, "Firma del cliente: _______________________")

    p.showPage()
    p.save()
    return response

@login_required
def factura_create_from_contrato(request, contrato_pk):
    contrato = get_object_or_404(Contrato, pk=contrato_pk)
    cliente = None
    reserva = contrato.reserva
    if reserva:
        cliente = reserva.cliente

    if request.method == 'POST':
        form = FacturaForm(request.POST)
        if form.is_valid():
            factura = form.save(commit=False)
            factura.contrato = contrato
            factura.fecha_emision = timezone.now()
            # Generación automática del número de factura
            año_actual = timezone.now().year
            ultima_factura = Factura.objects.filter(numero_factura__startswith=f'F{año_actual}').order_by('-numero_factura').first()
            if ultima_factura:
                try:
                    ultimo_numero = int(ultima_factura.numero_factura.split('-')[-1])
                except Exception:
                    ultimo_numero = 0
                nuevo_numero = ultimo_numero + 1
            else:
                nuevo_numero = 1
            factura.numero_factura = f'F{año_actual}-{nuevo_numero:06d}'
            if not factura.fecha_vencimiento:
                factura.fecha_vencimiento = factura.fecha_emision.date() + timezone.timedelta(days=30)
            factura.save()
            messages.success(request, 'Factura creada exitosamente.')
            return redirect('alquiler:factura_detail', pk=factura.pk)
    else:
        # Precarga automática
        initial = {
            'contrato': contrato.pk,
            'rut_receptor': cliente.rut_empresa if cliente else '',
            'razon_social_receptor': cliente.razon_social if cliente else '',
            'giro_receptor': cliente.giro if cliente else '',
            'direccion_receptor': cliente.direccion if cliente else '',
            'subtotal': round(reserva.monto_total / Decimal('1.19'), 2) if reserva else 0,
            'iva': round(reserva.monto_total - (reserva.monto_total / Decimal('1.19')), 2) if reserva else 0,
            'total': reserva.monto_total if reserva else 0,
            'fecha_vencimiento': timezone.now().date() + timezone.timedelta(days=30),
        }
        form = FacturaForm(initial=initial)
    return render(request, 'alquiler/factura_form.html', {
        'form': form,
        'title': f'Nueva Factura para Contrato {contrato.numero_contrato}',
        'from_contrato': True,
        'contrato': contrato,
    })

@login_required
@require_http_methods(["POST"])
def factura_anular(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    if factura.estado != 'ANULADA':
        factura.estado = 'ANULADA'
        factura.save()
        # Aquí podrías crear la lógica para generar la nota de crédito asociada
        messages.success(request, 'Factura anulada exitosamente. Debe generarse una nota de crédito.')
    else:
        messages.warning(request, 'La factura ya está anulada.')
    return redirect('alquiler:factura_detail', pk=pk)

@login_required
def factura_update(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    if factura.estado != 'BORRADOR':
        messages.error(request, "Solo se pueden editar facturas en estado BORRADOR.")
        return redirect('alquiler:factura_detail', pk=pk)
    if request.method == 'POST':
        form = FacturaForm(request.POST, instance=factura)
        if form.is_valid():
            form.save()
            messages.success(request, 'Factura actualizada exitosamente.')
            return redirect('alquiler:factura_detail', pk=pk)
    else:
        form = FacturaForm(instance=factura)
    return render(request, 'alquiler/factura_form.html', {
        'form': form,
        'factura': factura,
        'title': 'Editar Factura'
    })

# CRUD NOTAS
@login_required
def nota_create(request, factura_pk):
    factura = get_object_or_404(Factura, pk=factura_pk)
    tipo = request.GET.get('tipo')
    initial_data = {}
    if tipo in ('CREDITO', 'DEBITO'):
        initial_data['tipo'] = tipo
    if request.method == 'POST':
        form = NotaForm(request.POST)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.factura = factura
            # Generar número de nota automáticamente
            año_actual = timezone.now().year
            tipo_prefijo = 'NC' if nota.tipo == 'CREDITO' else 'ND'
            ultima_nota = Nota.objects.filter(tipo=nota.tipo, numero__startswith=f'{tipo_prefijo}{año_actual}').order_by('-numero').first()
            if ultima_nota:
                try:
                    ultimo_numero = int(ultima_nota.numero.split('-')[-1])
                except Exception:
                    ultimo_numero = 0
                nuevo_numero = ultimo_numero + 1
            else:
                nuevo_numero = 1
            nota.numero = f'{tipo_prefijo}{año_actual}-{nuevo_numero:06d}'
            nota.save()
            messages.success(request, f'Nota de {"crédito" if nota.tipo == "CREDITO" else "débito"} creada exitosamente.')
            return redirect('alquiler:factura_detail', pk=factura.pk)
    else:
        form = NotaForm(initial=initial_data)
    return render(request, 'alquiler/nota_form.html', {
        'form': form,
        'factura': factura,
    })

@login_required
def nota_detail(request, pk):
    nota = get_object_or_404(Nota, pk=pk)
    return render(request, 'alquiler/nota_detail.html', {
        'nota': nota,
    })

from django.http import JsonResponse
from .models import Contrato

def api_datos_contrato(request, contrato_id):
    try:
        contrato = Contrato.objects.select_related('cliente').get(pk=contrato_id)
        data = {
            "cliente": {
                "rut": contrato.cliente.rut_empresa or contrato.cliente.numero_documento or "",
                "razon_social": contrato.cliente.razon_social or "",
                "giro": contrato.cliente.giro or "",
                "direccion": contrato.cliente.direccion or "",
            },
            "subtotal": float(contrato.monto_total) if hasattr(contrato, "monto_total") else "",
        }
    except Contrato.DoesNotExist:
        data = {}
    return JsonResponse(data)

# VISTA PARA EL DASHBOARD DE ALQUILER
class AlquilerDashboardView(TemplateView):
    template_name = "alquiler/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoy = timezone.now().date()
        mes_actual = hoy.month
        anio_actual = hoy.year

        # KPIs
        context["total_reservas_hoy"] = Reserva.objects.filter(fecha_reserva__date=hoy).count()
        context["total_reservas_mes"] = Reserva.objects.filter(
            fecha_reserva__year=anio_actual, fecha_reserva__month=mes_actual
        ).count()
        context["total_reservas"] = Reserva.objects.count()
        context["reservas_por_estado"] = Reserva.objects.values("estado").annotate(cantidad=Count("id"))
        context["contratos_activos"] = Contrato.objects.filter(estado__in=["ACTIVO", "FIRMADO"]).count()
        context["facturas_emitidas"] = Factura.objects.count()
        context["facturas_pendientes"] = Factura.objects.exclude(estado="PAGADA").count()
        context["proximas_reservas"] = Reserva.objects.filter(
            fecha_inicio__gte=timezone.now()
        ).order_by("fecha_inicio")[:5]
        return context