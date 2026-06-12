"""
Aplicación Flask del turnero para el Certificado de Antecedentes (Policía de Río Negro).

Define las rutas públicas (formulario de turnos y API de horarios) y las del panel
de administración. Toda la lógica se delega en los controladores de `lib.controladores`.
"""

import os
import secrets

from flask import Flask, render_template, request, session, abort

from lib.database import inicializar_bd
from lib.controladores import (
    procesar_inicio_formulario, obtener_horarios_json, procesar_envio_turno,
    redirigir_admin, mostrar_login_admin, procesar_login_admin,
    mostrar_turnos_admin, procesar_borrado_turno, cerrar_sesion_admin,
)
from lib.config import SECRET_KEY, DATABASE_PATH

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Tolerar la barra final en las URLs (ej. /admin y /admin/ funcionan igual).
app.url_map.strict_slashes = False

# Inicializar la base de datos física al arrancar si el archivo no existe
if not os.path.exists(DATABASE_PATH):
    inicializar_bd()


# --- Protección CSRF ---
# Token aleatorio por sesión que viaja en cada formulario (campo oculto o cabecera)
# y se valida en todo POST. Sin él, un sitio externo no puede forzar peticiones.

def obtener_csrf_token():
    """Devuelve el token CSRF de la sesión, creándolo la primera vez."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    return session["csrf_token"]


@app.context_processor
def inyectar_csrf_token():
    """Expone `csrf_token()` a todas las plantillas Jinja."""
    return {"csrf_token": obtener_csrf_token}


@app.before_request
def validar_csrf():
    """Rechaza con 400 cualquier POST cuyo token CSRF falte o no coincida."""
    if request.method == "POST":
        token_sesion = session.get("csrf_token")
        # El token llega por el formulario (campo oculto) o por cabecera (peticiones fetch).
        token_enviado = request.form.get("csrf_token") or request.headers.get("X-CSRFToken")
        # Usamos compare_digest en vez de "==" porque es la forma segura de comparar tokens.
        if not token_sesion or not secrets.compare_digest(token_sesion, token_enviado or ""):
            abort(400)


@app.route('/')
def formulario():
    """Vista pública: muestra el formulario de reserva de turnos."""
    contexto = procesar_inicio_formulario()
    return render_template('formulario.html', contexto=contexto)

@app.route('/api/horarios-disponibles')
def horarios_json():
    """API JSON con los horarios disponibles de una fecha (consumida por Alpine.js)."""
    return obtener_horarios_json()

@app.route('/sacar-turno', methods=['POST'])
def sacar_turno():
    """Procesa el alta de un turno enviado desde el formulario público."""
    return procesar_envio_turno()

@app.route('/admin')
def admin_index():
    """Entrada al panel: redirige al listado si hay sesión, o al login si no."""
    return redirigir_admin()

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Muestra (GET) o valida (POST) el formulario de acceso al panel."""
    if request.method == 'POST':
        return procesar_login_admin()
    return mostrar_login_admin()

@app.route('/admin/turnos')
def admin_turnos():
    """Panel protegido: lista los turnos registrados."""
    return mostrar_turnos_admin()

@app.route('/admin/borrar/<int:turno_id>', methods=['POST'])
def admin_borrar(turno_id):
    """Elimina un turno por su id (acción protegida del panel)."""
    return procesar_borrado_turno(turno_id)

@app.route('/admin/logout')
def admin_logout():
    """Cierra la sesión del administrador."""
    return cerrar_sesion_admin()

@app.errorhandler(404)
def page_not_found(e):
    """Renderiza la página de error 404 personalizada."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, port=3000)