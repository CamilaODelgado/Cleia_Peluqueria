// ===============================================
// 1. FUNCIÓN DE UTILIDAD: OBTENER EL TOKEN CSRF
// ===============================================

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ===============================================
// 2. LÓGICA PRINCIPAL: VALIDACIÓN Y ENVÍO DEL FORMULARIO
// ===============================================

document.addEventListener('DOMContentLoaded', function() {
    const formulario = document.getElementById('formulario');

    // Función de ayuda para manejar la clase de error visual
    const toggleErrorClass = (elemento, add) => {
        if (add) {
            elemento.classList.add('error-border');
        } else {
            elemento.classList.remove('error-border');
        }
    };

    formulario.addEventListener('submit', function(e) {
        e.preventDefault(); // Detiene el envío HTTP tradicional
        
        let esValido = true;
        let camposVacios = [];
        
        // Referencias de los campos
        const nombreInput = document.getElementById('nombre');
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        const password2Input = document.getElementById('password2');
        
        // Array de campos obligatorios para iterar
        const camposObligatorios = [
            { elemento: nombreInput, nombre: 'Nombre' },
            { elemento: emailInput, nombre: 'Email' },
            { elemento: passwordInput, nombre: 'Contraseña' },
            { elemento: password2Input, nombre: 'Confirma Contraseña' },
        ];

        // Reiniciar estado de validez
        esValido = true;
        camposVacios = [];
        
        // --- VALIDACIÓN 1: CAMPOS VACÍOS ---
        camposObligatorios.forEach(campo => {
            if (campo.elemento.value.trim() === '') {
                esValido = false;
                camposVacios.push(campo.nombre);
                toggleErrorClass(campo.elemento, true);
            } else {
                toggleErrorClass(campo.elemento, false);
            }
        });

        // --- VALIDACIÓN 2: COINCIDENCIA DE CONTRASEÑAS ---
        if (passwordInput.value !== password2Input.value) {
            // Solo si las contraseñas tienen contenido y no coinciden, es un error
            if (passwordInput.value.trim() !== '' && password2Input.value.trim() !== '') {
                esValido = false;
            }
            toggleErrorClass(passwordInput, true); 
            toggleErrorClass(password2Input, true);
        } else {
            // Quita error si coinciden y no están vacías
            if (passwordInput.value.trim() !== '') {
                toggleErrorClass(passwordInput, false); 
                toggleErrorClass(password2Input, false);
            }
        }


        // 3. MANEJO DE ERRORES FRONTEND
        if (!esValido) {
            if (camposVacios.length > 0) {
                alert(`Por favor, complete los campos: ${camposVacios.join(', ')}`);
            } else if (passwordInput.value !== password2Input.value) {
                alert("Las contraseñas no coinciden. Por favor, revíselas.");
            }
            
            // Enfocar el primer campo con error
            const primerCampoConError = camposObligatorios.find(campo => campo.elemento.classList.contains('error-border'));
            if (primerCampoConError) {
                primerCampoConError.elemento.focus();
            }

        } 
        // 4. ENVÍO VÍA FETCH A DJANGO
        else {
            const csrftoken = getCookie('csrftoken'); 
            const data = new FormData(formulario); 

            fetch(formulario.action, {
                method: formulario.method,
                body: data,
                headers: {
                    'X-CSRFToken': csrftoken, 
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            // -------------------------------------------------------------
            // CAMBIO CRÍTICO AQUÍ: Asegurar que se lea el JSON
            // -------------------------------------------------------------
            .then(response => {
                // Siempre lee la respuesta como JSON, sin importar si es 200 o 400.
                return response.json().then(data => ({
                    status: response.status,
                    ok: response.ok,
                    data: data 
                }));
            })
            .then(res => {
                // Ahora, res.data contiene el JSON, y res.ok indica el estado HTTP
                
                // 1. Si el estado HTTP fue bueno (200-299) Y el success del JSON es true
                if (res.ok && res.data.success) { 
                    alert("¡Tu cuenta fue registrada exitosamente!");
                    // REDIRECCIÓN FINAL
                    window.location.href = '/login'; // <-- AJUSTA ESTA URL
                    
                } 
                // 2. Si el estado HTTP fue 400, o success: false
                else {
                    const mensaje = res.data.message || "Error desconocido. Intente de nuevo.";
                    
                    // Manejar errores de campo específicos si Django los devolvió
                    if (res.data.errors) {
                        const errores = Object.values(res.data.errors).flat().join('\n');
                        alert(`Error de validación:\n${errores}`);
                    } else {
                        alert(`Error en el registro: ${mensaje}`); 
                    }
                }
            })
            // -------------------------------------------------------------
            // CATCH solo para fallos de red/conexión, no para errores 400 de Django
            // -------------------------------------------------------------
            .catch(error => {
                console.error('Error de conexión o fallo no esperado:', error);
                alert('Ocurrió un error de conexión. Verifique su red y el servidor.');
            });
        }
    });
});