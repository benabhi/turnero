"""Lógica de fechas y horarios: límites del calendario, días hábiles y grilla de turnos."""

from datetime import datetime, timedelta

from lib.config import BLOQUES_HORARIOS, DIAS_MAXIMO_RESERVA

def obtener_limites_calendario():
    """Devuelve `(min_fecha, max_fecha)` en formato `YYYY-MM-DD`: desde hoy hasta hoy + `DIAS_MAXIMO_RESERVA`."""
    ahora = datetime.now()
    min_fecha = ahora.strftime('%Y-%m-%d')
    max_fecha = (ahora + timedelta(days=DIAS_MAXIMO_RESERVA)).strftime('%Y-%m-%d')
    return min_fecha, max_fecha

def verificar_fin_de_semana(fecha_str):
    """Indica si la fecha `YYYY-MM-DD` cae sábado o domingo (`False` si el formato es inválido)."""
    try:
        dt = datetime.strptime(fecha_str, '%Y-%m-%d')
        # weekday() numera los días desde lunes=0; 5 y 6 son sábado y domingo.
        return dt.weekday() in (5, 6)
    except ValueError:
        return False

def generar_grilla_base(fecha_objetivo_str, horas_reservadas):
    """
    Arma la grilla de horarios de una fecha como lista de dicts `{hora, disponible, mensaje}`.

    Marca cada bloque como no disponible si ya está reservado o si la hora ya pasó (solo hoy).
    """
    ahora = datetime.now()
    hoy_str = ahora.strftime('%Y-%m-%d')
    hora_actual_str = ahora.strftime('%H:%M')

    horarios_mapeados = []

    for bloque_hora in BLOQUES_HORARIOS:
        # Evaluamos las condiciones de forma independiente
        if bloque_hora in horas_reservadas:
            esta_disponible = False
            texto_mensaje = "(Reservado)"
        elif fecha_objetivo_str == hoy_str and bloque_hora <= hora_actual_str:
            esta_disponible = False
            texto_mensaje = "(No Disponible)"
        else:
            esta_disponible = True
            texto_mensaje = "(Disponible)"

        # Estructura limpia y plana sin variables intermedias cruzadas
        item_horario = {
            "hora": str(bloque_hora),
            "disponible": bool(esta_disponible),
            "mensaje": str(texto_mensaje)
        }

        horarios_mapeados.append(item_horario)

    return horarios_mapeados