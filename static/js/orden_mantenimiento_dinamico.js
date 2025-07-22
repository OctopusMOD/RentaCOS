// AJAX para detalle de vehículo
document.addEventListener('DOMContentLoaded', function () {
    const patenteSelect = document.getElementById('id_vehiculo');
    if (patenteSelect) {
        patenteSelect.addEventListener('change', function () {
            const vehiculoId = this.value;
            if (vehiculoId) {
                fetch(`/mantenimiento/vehiculo_info/?vehiculo_id=${vehiculoId}`)
                    .then(response => response.json())
                    .then(data => {
                        let html = '';
                        if (data.error) {
                            html = `<span class="text-danger">${data.error}</span>`;
                        } else {
                            html = `
                                <ul class="list-unstyled">
                                    <li><strong>Marca:</strong> ${data.marca || ''}</li>
                                    <li><strong>Modelo:</strong> ${data.modelo || ''}</li>
                                    <li><strong>Año:</strong> ${data.anio_modelo || ''}</li>
                                    <li><strong>Tracción:</strong> ${data.traccion || ''}</li>
                                    <li><strong>VIN:</strong> ${data.vin || ''}</li>
                                    <li><strong>Color:</strong> ${data.color || ''}</li>
                                    <li><strong>Cliente:</strong> ${data.cliente || '-'}</li>
                                </ul>
                            `;
                        }
                        document.getElementById('vehiculo-info').innerHTML = html;
                    });
            } else {
                document.getElementById('vehiculo-info').innerHTML = '<span class="text-muted">Seleccione una patente para ver los datos.</span>';
            }
        });

        // Dispara el cambio al cargar si hay valor seleccionado
        if (patenteSelect.value) {
            patenteSelect.dispatchEvent(new Event('change'));
        }
    }

    // Preview de número de OT (solo como sugerencia)
    const previewSpan = document.getElementById('preview-ot-numero');
    if (previewSpan) {
        fetch('/mantenimiento/next_ot_numero/')
            .then(r => r.json())
            .then(data => {
                previewSpan.textContent = data.numero_orden || '(Pendiente)';
            });
    }
});
// Este archivo agrega funcionalidad dinámica a los formsets de trabajos realizados y repuestos/insumos
// Requiere que los IDs de las tablas sean 'trabajos-table' y 'repuestos-table'
// Requiere que los formsets tengan el atributo 'prefix' (ej: 'trabajos', 'repuestos')

// Funciones para agregar/eliminar filas y calcular totales en los formsets de Django

// Agregar fila al formset de trabajos realizados
function addTrabajoRow() {
    addFormRow('trabajos');
}

// Agregar fila al formset de repuestos/insumos
function addRepuestoRow() {
    addFormRow('repuestos');
}

// Eliminar fila (funciona para ambos formsets)
function deleteRow(btn) {
    // Encuentra el <tr>
    let tr = btn.closest('tr');
    // Marca el DELETE si existe el campo DELETE (para Django)
    let delInput = tr.querySelector('input[type="checkbox"][name*="DELETE"]');
    if (delInput) {
        delInput.checked = true;
        tr.style.display = 'none';
    } else {
        // Si no hay campo DELETE, elimina la fila directamente (para filas nuevas)
        tr.remove();
    }
    updateTotals();
}

// Función genérica para agregar filas a un formset
function addFormRow(prefix) {
    let tbody = document.getElementById(prefix + '-tbody');
    let formIdxInput = document.querySelector('input[name="' + prefix + '-TOTAL_FORMS"]');
    if (!formIdxInput) {
        alert('No se encontró el input ' + prefix + '-TOTAL_FORMS');
        return;
    }
    let formIdx = parseInt(formIdxInput.value);

    // Busca la primera fila como base (puede estar oculta pero sirve como template)
    let templateRow = tbody.querySelector('tr');
    if (!templateRow) return;

    // Clona la fila
    let newRow = templateRow.cloneNode(true);

    // Limpia los valores de los inputs y actualiza sus nombres/ids
    let inputs = newRow.querySelectorAll('input,select,textarea');
    inputs.forEach(function(input) {
        // Actualiza el name y id con el nuevo índice
        if (input.name) {
            input.name = input.name.replace(new RegExp(prefix + '-\\d+-'), prefix + '-' + formIdx + '-');
        }
        if (input.id) {
            input.id = input.id.replace(new RegExp(prefix + '-\\d+-'), prefix + '-' + formIdx + '-');
        }
        // Limpia el valor (excepto campos ocultos DELETE)
        if (input.type === 'checkbox' && input.name.indexOf('DELETE') !== -1) {
            input.checked = false;
        } else if (input.type === 'hidden') {
            if (input.name.indexOf('DELETE') !== -1) {
                input.value = '';
            } else if (input.name.indexOf('id') !== -1) {
                input.value = '';
            }
        } else {
            input.value = '';
        }
    });

    // Muestra la fila (por si estaba oculta)
    newRow.style.display = '';

    // Agrega la fila al tbody
    tbody.appendChild(newRow);

    // Incrementa el TOTAL_FORMS
    formIdxInput.value = formIdx + 1;

    // Actualiza los totales
    updateTotals();
}

// Calcula los totales de las tablas al cambiar unidades o valor
function updateTotals() {
    ['trabajos', 'repuestos'].forEach(function(prefix) {
        let table = document.getElementById(prefix + '-table');
        if (!table) return;
        let rows = table.querySelectorAll('tbody tr');
        rows.forEach(function(row) {
            // Solo filas visibles/no eliminadas
            if (row.style.display === 'none') return;
            let unidades = row.querySelector('input[name$="unidades"], input[name$="cantidad"]');
            let valor = row.querySelector('input[name$="valor_unitario"]');
            let totalCell = row.querySelector('td:last-child').previousElementSibling; // penúltima columna
            let u = parseFloat(unidades ? unidades.value : 0) || 0;
            let v = parseFloat(valor ? valor.value : 0) || 0;
            let t = (u * v).toFixed(2);
            if (totalCell) totalCell.textContent = t;
        });
    });
}

// Auto-actualiza totales al cambiar unidades o valor
document.addEventListener('input', function(e) {
    if (
        e.target.name && (
            e.target.name.endsWith('unidades') ||
            e.target.name.endsWith('cantidad') ||
            e.target.name.endsWith('valor_unitario')
        )
    ) {
        updateTotals();
    }
});

// Inicializa los totales al cargar la página
window.addEventListener('DOMContentLoaded', updateTotals);