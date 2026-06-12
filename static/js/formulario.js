// Componente Alpine para el formulario de turnos.
// Recibe los valores iniciales renderizados por el servidor (Jinja).
document.addEventListener('alpine:init', () => {
    Alpine.data('formTurno', (fechaInicial = '', esFinDeSemanaInicial = false) => ({
        fecha: fechaInicial,
        esFinDeSemana: esFinDeSemanaInicial,
        horarios: [],

        // Alpine llama a init() automáticamente al montar el componente.
        init() {
            this.actualizarHorarios();
        },

        async actualizarHorarios() {
            if (!this.fecha) return;
            try {
                const respuesta = await fetch(`/api/horarios-disponibles?fecha=${this.fecha}`);
                const datos = await respuesta.json();
                this.esFinDeSemana = datos.es_fin_de_semana;
                this.horarios = datos.horarios;
            } catch (error) {
                console.error('Error al recuperar horarios mediante AJAX:', error);
            }
        }
    }));
});
