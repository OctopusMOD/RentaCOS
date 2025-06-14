document.addEventListener('DOMContentLoaded', function() {
console.log("tipo_cliente_toggle.js cargado");
    const tipoClienteSelect = document.getElementById('id_tipo_cliente');
    const empresaFields = document.querySelectorAll('.empresa-field');
    const personaFields = document.querySelectorAll('.persona-field');

    function toggleFields() {
        if (!tipoClienteSelect) return;
        if (tipoClienteSelect.value === 'EMPRESA') {
            empresaFields.forEach(el => el.style.display = '');
            personaFields.forEach(el => el.style.display = 'none');
        } else {
            empresaFields.forEach(el => el.style.display = 'none');
            personaFields.forEach(el => el.style.display = '');
        }
    }

    if (tipoClienteSelect) {
        tipoClienteSelect.addEventListener('change', toggleFields);
        toggleFields();
    }
});