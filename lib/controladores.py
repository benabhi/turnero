"""
Controladores de la aplicación: reciben la petición, aplican la lógica y devuelven la respuesta.

Agrupa los controladores de la vista pública (formulario, API de horarios, alta de turno)
y los del panel de administración (login, listado, borrado, logout).
"""

import re

from flask import request, jsonify, render_template, session, redirect

from lib.database import obtener_horas_reservadas, guardar_turno, obtener_turnos, borrar_turno
from lib.fechas import obtener_limites_calendario, verificar_fin_de_semana, generar_grilla_base
from lib.config import BLOQUES_HORARIOS, ADMIN_USUARIO, ADMIN_CLAVE

# Campos que viajan en el formulario, en orden.
CAMPOS = ("fecha", "hora", "nombre", "apellido", "dni", "telefono", "email")


def _construir_horarios(fecha):
    """Devuelve `(es_fin_de_semana, grilla_de_horarios)` para una fecha dada."""
    if verificar_fin_de_semana(fecha):
        return True, []
    horas_ocupadas = obtener_horas_reservadas(fecha)
    return False, generar_grilla_base(fecha, horas_ocupadas)


def _construir_contexto(fecha, errores=None, datos=None):
    """Arma el contexto que consume `formulario.html` (carga inicial o re-render con errores)."""
    datos = datos or {}
    min_fecha, max_fecha = obtener_limites_calendario()
    es_fin_de_semana, horarios = _construir_horarios(fecha)

    return {
        "min_fecha": min_fecha,
        "max_fecha": max_fecha,
        "es_fin_de_semana": es_fin_de_semana,
        "horarios": horarios,
        "errores": errores or {},
        "previo_fecha": fecha,
        "previo_hora": datos.get("hora", ""),
        "previo_nombre": datos.get("nombre", ""),
        "previo_apellido": datos.get("apellido", ""),
        "previo_dni": datos.get("dni", ""),
        "previo_telefono": datos.get("telefono", ""),
        "previo_email": datos.get("email", ""),
    }


def procesar_inicio_formulario():
    """Carga inicial de la vista pública (`GET /`)."""
    min_fecha, _ = obtener_limites_calendario()
    fecha = request.args.get("fecha", min_fecha)
    return _construir_contexto(fecha)


def obtener_horarios_json():
    """API de horarios (`GET /api/horarios-disponibles`) que consume Alpine.js."""
    fecha = request.args.get("fecha")
    if not fecha:
        return jsonify({"error": "Fecha requerida"}), 400

    es_fin_de_semana, horarios = _construir_horarios(fecha)
    return jsonify({"es_fin_de_semana": es_fin_de_semana, "horarios": horarios})


def _validar(datos):
    """Valida los datos del turno y devuelve un diccionario `{campo: mensaje}`. Vacío = todo OK."""
    errores = {}
    min_fecha, max_fecha = obtener_limites_calendario()
    fecha = datos["fecha"]

    # Fecha: presente, dentro de rango y día hábil.
    if not fecha:
        errores["fecha"] = "Seleccione una fecha."
    elif not (min_fecha <= fecha <= max_fecha):
        errores["fecha"] = "La fecha está fuera del rango permitido."
    elif verificar_fin_de_semana(fecha):
        errores["fecha"] = "No hay atención sábados ni domingos."

    # Hora: presente, válida y todavía disponible (solo si la fecha es válida).
    hora = datos["hora"]
    if not hora:
        errores["hora"] = "Seleccione un horario."
    elif hora not in BLOQUES_HORARIOS:
        errores["hora"] = "Horario inválido."
    elif "fecha" not in errores:
        _, horarios = _construir_horarios(fecha)
        # Comprensión de conjunto: arma un set con la 'hora' de cada horario que esté disponible.
        disponibles = {h["hora"] for h in horarios if h["disponible"]}
        if hora not in disponibles:
            errores["hora"] = "Ese horario ya no está disponible."

    # Datos personales.
    if not re.fullmatch(r"[A-Za-zÀ-ÿ' \-]+", datos["nombre"]):
        errores["nombre"] = "Nombre inválido (solo letras)."
    if not re.fullmatch(r"[A-Za-zÀ-ÿ' \-]+", datos["apellido"]):
        errores["apellido"] = "Apellido inválido (solo letras)."
    if not re.fullmatch(r"\d{7,9}", datos["dni"]):
        errores["dni"] = "DNI inválido (7 a 9 dígitos, sin puntos)."
    if not re.fullmatch(r"\d{6,15}", datos["telefono"]):
        errores["telefono"] = "Teléfono inválido (solo números)."
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", datos["email"]):
        errores["email"] = "Correo electrónico inválido."

    return errores


def procesar_envio_turno():
    """Procesa el alta de un turno (`POST /sacar-turno`)."""
    # Comprensión de diccionario: arma un dict con cada campo y su valor del formulario (sin espacios).
    datos = {campo: request.form.get(campo, "").strip() for campo in CAMPOS}
    errores = _validar(datos)

    if not errores:
        exito = guardar_turno(
            datos["fecha"], datos["hora"], datos["nombre"], datos["apellido"],
            datos["dni"], datos["telefono"], datos["email"],
        )
        if exito:
            return render_template("respuesta.html", turno=datos)
        # Si llegó acá, otro usuario reservó esta misma fecha y hora un instante antes:
        # la base de datos rechazó el duplicado (regla UNIQUE de fecha+hora).
        errores["hora"] = "Ese horario acaba de ser reservado. Elija otro."

    contexto = _construir_contexto(datos["fecha"], errores, datos)
    return render_template("formulario.html", contexto=contexto)


# --- Panel de administración ---

def redirigir_admin():
    """`GET /admin`: lleva al panel si hay sesión, o al login si no."""
    if session.get("admin"):
        return redirect("/admin/turnos")
    return redirect("/admin/login")


def mostrar_login_admin():
    """`GET /admin/login`: muestra el formulario (o salta al panel si ya hay sesión)."""
    if session.get("admin"):
        return redirect("/admin/turnos")
    return render_template("admin_login.html")


def procesar_login_admin():
    """`POST /admin/login`: valida credenciales. Responde al fetch del cliente."""
    usuario = request.form.get("usuario", "").strip()
    clave = request.form.get("clave", "")

    if usuario == ADMIN_USUARIO and clave == ADMIN_CLAVE:
        session["admin"] = True
        return ("", 204)  # OK: el JS del login redirige a /admin/turnos

    return jsonify({"clave": "Usuario o contraseña incorrectos."}), 401


def mostrar_turnos_admin():
    """`GET /admin/turnos`: lista los turnos (vigentes por defecto, o todos con `?historial=true`)."""
    if not session.get("admin"):
        return redirect("/admin/login")

    historial = request.args.get("historial") == "true"
    if historial:
        turnos = obtener_turnos()
    else:
        hoy, _ = obtener_limites_calendario()  # min_fecha == hoy
        turnos = obtener_turnos(desde=hoy)

    return render_template("admin_turnos.html", turnos=turnos, historial=historial)


def procesar_borrado_turno(turno_id):
    """`POST /admin/borrar/<id>`: elimina un turno. Responde al fetch del cliente."""
    if not session.get("admin"):
        return ("", 401)

    borrar_turno(turno_id)
    return ("", 204)


def cerrar_sesion_admin():
    """`GET /admin/logout`: cierra la sesión y vuelve al login."""
    session.pop("admin", None)
    return redirect("/admin/login")
