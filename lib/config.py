"""
Constantes y parámetros configurables de la aplicación.
Centralizar acá evita "números mágicos" repartidos por el código.
"""

# Clave para firmar sesiones y tokens CSRF.
# TODO: mover a variable de entorno (.env) más adelante.
SECRET_KEY: str = "dev-cambiar-esta-clave"

# Credenciales del panel de administración (hardcodeadas; mover a .env junto con SECRET_KEY).
# TODO: mover a variable de entorno (.env) más adelante.
ADMIN_USUARIO: str = "admin"
ADMIN_CLAVE: str = "123456"

# Ruta del archivo de base de datos SQLite.
DATABASE_PATH: str = "database.db"

# Cuántos días hacia adelante se puede reservar (ventana del calendario).
DIAS_MAXIMO_RESERVA: int = 30

# Grilla de horarios de atención: cada media hora, de 08:00 a 14:00.
BLOQUES_HORARIOS: list[str] = [
    "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
    "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00",
]
