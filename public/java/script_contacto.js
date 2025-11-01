document.addEventListener('DOMContentLoaded', function() {
    const formulario = document.getElementById('formulario');

    if (!formulario) return; // Evita errores si no existe el formulario

    formulario.addEventListener('submit', function(e) {
        e.preventDefault(); // Evitamos envío por defecto hasta validar

        let esValido = true;
        let camposVacios = [];

        // 1. OBTENER CAMPOS
        const nombreInput = document.getElementById('nombre');
        const emailInput = document.getElementById('email');
        const mensajeInput = document.getElementById('mensaje');

        const camposObligatorios = [
            { elemento: nombreInput, nombre: 'Nombre' },
            { elemento: emailInput, nombre: 'Email' },
            { elemento: mensajeInput, nombre: 'Mensaje' },
        ];

        // 2. VALIDACIÓN DE CAMPOS VACÍOS
        camposObligatorios.forEach(campo => {
            if (!campo.elemento || campo.elemento.value.trim() === '') {
                esValido = false;
                camposVacios.push(campo.nombre);
            }
        });

        if (!esValido) {
            alert("Por favor, complete los campos: " + camposVacios.join(', '));
            const primerCampoVacio = camposObligatorios.find(campo => campo.elemento && campo.elemento.value.trim() === '');
            if (primerCampoVacio) primerCampoVacio.elemento.focus();
            return; // Detenemos el envío
        }

        // 3. SI TODO ESTÁ OK → ENVIAR DATOS
        const formData = new FormData(formulario);
        formData.append("access_key", "e244de70-56d2-4e1c-b9d8-7869644f9bd5");

        const submitButton = formulario.querySelector('button[type="submit"]');
        submitButton.textContent = 'Enviando...';
        submitButton.disabled = true;

        fetch(formulario.action, {
            method: formulario.method,
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`¡Tu mensaje fue enviado exitosamente, ${nombreInput.value}!`);
                formulario.reset();
            } else {
                console.error('Error del servidor de Web3Forms:', data.message);
                alert(`Error al enviar: ${data.message}. Por favor, revisa la consola.`);
            }
        })
        .catch(error => {
            console.error('Error de conexión o fetch:', error);
            alert('Hubo un error de conexión. Inténtalo de nuevo.');
        })
        .finally(() => {
            submitButton.textContent = 'Enviar Mensaje';
            submitButton.disabled = false;
        });
    });
});
