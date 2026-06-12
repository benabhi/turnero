"""Capa de acceso a datos (SQLite): conexión, creación de la tabla y operaciones sobre turnos."""

import sqlite3
from contextlib import closing

from lib.config import DATABASE_PATH

def obtener_conexion():
    """Abre una conexión a la base con filas accesibles por nombre de columna (`sqlite3.Row`)."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_bd():
    """Crea la tabla `turnos` si no existe (incluye el `UNIQUE` de fecha+hora)."""
    with closing(obtener_conexion()) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS turnos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                hora TEXT NOT NULL,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                dni TEXT NOT NULL,
                telefono TEXT NOT NULL,
                email TEXT NOT NULL,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fecha, hora)
            )
        ''')
        conn.commit()

def obtener_horas_reservadas(fecha_str):
    """
    Retorna un `set` (evita duplicidad) de horas reservadas para una fecha dada.
    Ejemplo de retorno: `{'08:30', '11:00'}`
    """
    with closing(obtener_conexion()) as conn:
        cursor = conn.execute("SELECT hora FROM turnos WHERE fecha = ?", (fecha_str,))
        # Guardamos en un set directo para búsquedas ultra rápidas.
        # Comprensión de conjunto: arma un set recorriendo cada fila y tomando su columna 'hora'.
        return {row['hora'] for row in cursor.fetchall()}

def guardar_turno(fecha, hora, nombre, apellido, dni, telefono, email):
    """Inserta de forma segura un nuevo turno confirmado en la base de datos."""
    with closing(obtener_conexion()) as conn:
        try:
            conn.execute('''
                INSERT INTO turnos (fecha, hora, nombre, apellido, dni, telefono, email)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (fecha, hora, nombre, apellido, dni, telefono, email))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def obtener_turnos(desde=None):
    """
    Lista los turnos ordenados por fecha y hora.
    Si se pasa `desde` (`YYYY-MM-DD`), filtra solo los turnos vigentes (`fecha >= desde`).
    """
    with closing(obtener_conexion()) as conn:
        if desde:
            cursor = conn.execute(
                "SELECT * FROM turnos WHERE fecha >= ? ORDER BY fecha, hora", (desde,)
            )
        else:
            cursor = conn.execute("SELECT * FROM turnos ORDER BY fecha, hora")
        return cursor.fetchall()

def borrar_turno(turno_id):
    """Elimina un turno por su id."""
    with closing(obtener_conexion()) as conn:
        conn.execute("DELETE FROM turnos WHERE id = ?", (turno_id,))
        conn.commit()