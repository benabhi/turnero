# Turnero - Certificado de Antecedentes (Policía de Río Negro)

Aplicación web para reservar turnos del trámite de **Certificado de Antecedentes**.
Permite al ciudadano elegir fecha y horario disponible (cada media hora, de 08:00 a
14:00, días hábiles, hasta un mes a futuro) y cuenta con un panel de administración
para ver y eliminar turnos.

> **Material con fines didácticos**, desarrollado para la materia **Sistemas de
> Información 2** (Tecnicatura/Analista de Sistemas). No es un sistema en producción.

## Tecnologías

- **Python 3** + **Flask** (backend y templates Jinja2)
- **SQLite** (base de datos en archivo, sin servidor)
- **Alpine.js** (interactividad mínima en el formulario)

## Puesta en marcha

```bash
# 1. Crear y activar el entorno virtual
python -m venv venv
venv\Scripts\activate        # En Linux/Mac: source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Levantar la aplicación
python app.py
```

La app queda disponible en **http://localhost:3000**.

- Formulario público: `/`
- Panel de administración: `/admin` (usuario: `admin` / clave: `123456`)

## Estructura del proyecto

```
turnero/
├── app.py                 # Rutas Flask y arranque de la aplicación
├── requirements.txt       # Dependencias
├── lib/
│   ├── config.py          # Constantes (horarios, credenciales, clave secreta)
│   ├── database.py        # Acceso a la base SQLite (consultas y alta/baja)
│   ├── fechas.py          # Lógica de fechas: rango, días hábiles y grilla de horarios
│   └── controladores.py   # Controladores: validan, procesan y arman la respuesta
├── templates/
│   ├── layout.html        # Plantilla base (navbar, estilos, scripts)
│   ├── formulario.html    # Formulario público de reserva
│   ├── respuesta.html     # Comprobante del turno confirmado
│   ├── admin_login.html   # Acceso al panel
│   ├── admin_turnos.html  # Listado de turnos (panel)
│   └── 404.html           # Página de error 404
└── static/
    ├── css/estilos.css    # Estilos
    └── js/
        ├── vendor/        # Librerías de terceros (Alpine.js)
        ├── formulario.js  # Componente Alpine del formulario público
        ├── admin_login.js # Lógica del acceso al panel
        └── admin_turnos.js# Borrado de turnos en el panel
```

## Dependencias

La única dependencia directa es **Flask**; el resto (Werkzeug, Jinja2, etc.) se
instalan automáticamente con él. Las versiones exactas están fijadas en
`requirements.txt` para reproducir el entorno.

## Documentación con pdoc

El código está documentado con *docstrings*. La documentación HTML se genera con
[pdoc](https://pdoc.dev/), que **no está en `requirements.txt`** por ser una herramienta
solo para documentar (la app no la necesita para funcionar):

```bash
pip install pdoc
pdoc app lib.config lib.fechas lib.database lib.controladores -o docs
```

Genera un sitio HTML en `docs/` (ignorada por git); abrí `docs/index.html` en el navegador.
