document.addEventListener('DOMContentLoaded', function () {
    // ---- Funciones para la tabla de repuestos ----
    const repuestosTbody = document.getElementById('repuestos-tbody');
    const totalRepuestosInput = document.getElementById('id_repuestos-TOTAL_FORMS');
    const addRepuestoBtn = document.getElementById('add-repuesto');

    // Función para crear una fila de repuesto
    function crearRepuestoRow(idx) {
        return `
        <tr>
            <td><input type="text" name="repuestos-${idx}-codigo" class="form-control"></td>
            <td><input type="text" name="repuestos-${idx}-descripcion" class="form-control"></td>
            <td><input type="number" name="repuestos-${idx}-valor" class="form-control repuesto-valor" min="0" value="0"></td>
            <td><input type="number" name="repuestos-${idx}-unidades" class="form-control repuesto-unidades" min="0" value="0"></td>
            <td><input type="text" name="repuestos-${idx}-valor_total" class="form-control repuesto-valor-total" readonly value="0"></td>
            <td><button type="button" class="btn btn-danger btn-sm remove-repuesto">Eliminar</button></td>
        </tr>`;
    }

    // Agregar repuesto
    if (addRepuestoBtn && repuestosTbody && totalRepuestosInput) {
        addRepuestoBtn.addEventListener('click', function () {
            const idx = parseInt(totalRepuestosInput.value);
            repuestosTbody.insertAdjacentHTML('beforeend', crearRepuestoRow(idx));
            totalRepuestosInput.value = idx + 1;
        });
    }

    // Eliminar repuesto
    repuestosTbody.addEventListener('click', function (e) {
        if (e.target && e.target.classList.contains('remove-repuesto')) {
            const row = e.target.closest('tr');
            row.parentNode.removeChild(row);
        }
    });

    // Actualizar valor total
    repuestosTbody.addEventListener('input', function (e) {
        if (e.target.classList.contains('repuesto-valor') || e.target.classList.contains('repuesto-unidades')) {
            const row = e.target.closest('tr');
            const valor = parseFloat(row.querySelector('.repuesto-valor').value) || 0;
            const unidades = parseFloat(row.querySelector('.repuesto-unidades').value) || 0;
            row.querySelector('.repuesto-valor-total').value = valor * unidades;
        }
    });
});