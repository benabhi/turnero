// Lógica del formulario de acceso al panel de control.
// Envía las credenciales por fetch y muestra los errores de validación
// debajo de cada campo sin recargar la página.
const btn = document.getElementById('btn-login');
const form = document.querySelector('form');

btn.addEventListener('click', async function () {
    document.querySelectorAll('.input-error').forEach(el => el.classList.remove('input-error'));
    document.querySelectorAll('.error-mensaje-input').forEach(el => el.remove());

    const formData = new FormData(form);

    try {
        // NOTE: URLSearchParams parsea las variables de un QueryString de la
        //       la URL a un objeto javascript, ej:  ?marca=casi se podria
        //       acceder con formData.get('marca');
        const response = await fetch('/admin/login', {
            method: 'POST',
            body: new URLSearchParams(formData)
        });

        if (response.ok) {
            // Credenciales válidas: Redirección física al panel de turnos
            window.location.href = '/admin/turnos';
        } else {
            // Error de credenciales (401 Unauthorized)
            const errores = await response.json();

            // Mensajes de error en formulario
            Object.keys(errores).forEach(campo => {
                const mensaje = errores[campo];
                if (mensaje) {
                    const inputElement = form.querySelector(`[name="${campo}"]`);
                    if (inputElement) {
                        inputElement.classList.add('input-error');
                        const errorSpan = document.createElement('span');
                        errorSpan.className = 'error-mensaje-input';
                        errorSpan.textContent = mensaje;
                        inputElement.parentNode.insertBefore(errorSpan, inputElement.nextSibling);
                    }
                }
            });
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error de conexión con el módulo de seguridad.');
    }
});
