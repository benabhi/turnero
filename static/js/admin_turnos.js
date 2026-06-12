// Borrado de turnos desde el panel de control.
// Intercepta el submit de cada fila, confirma con el operador y elimina el
// registro por fetch, quitando la fila de la tabla sin recargar la página.
document.querySelectorAll('.form-borrar-registro').forEach(form => {
    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const fila = this.closest('tr');
        const boton = this.querySelector('.btn-tabla-eliminar');
        const nombreCiudadano = fila.querySelector('.col-ciudadano').textContent;
        const url = this.getAttribute('action');

        if (confirm(`¿Está seguro de que desea eliminar el turno de ${nombreCiudadano}?`)) {

            boton.classList.add('baja-activa');
            boton.querySelector('.txt-eliminar').textContent = 'Borrando...';
            fila.classList.add('fila-flash-baja');

            const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrfToken }
                });

                if (response.ok) {
                    // Esperamos a que termine la animación CSS .fila-flash-baja
                    // (flashDesvanecer 0.4s en estilos.css) antes de quitar la fila;
                    // si cambia la duración de la animación, ajustar también este valor.
                    setTimeout(() => {
                        fila.remove();

                        // Sin filas restantes recargamos para que el servidor
                        // renderice el estado vacío ("no hay turnos").
                        const filasRestantes = document.querySelectorAll('.admin-table tbody tr');
                        if (filasRestantes.length === 0) {
                            window.location.reload();
                        }
                    }, 400);
                } else {
                    alert('No se pudo eliminar el registro en el servidor.');
                    boton.classList.remove('baja-activa');
                    boton.querySelector('.txt-eliminar').textContent = 'Eliminar';
                    fila.classList.remove('fila-flash-baja');
                }
            } catch (error) {
                console.error('Error en la conexión:', error);
                alert('Error de red al intentar borrar el turno.');
            }
        }
    });
});
