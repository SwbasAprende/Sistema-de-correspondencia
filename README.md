# Sistema de Correspondencia - CER 📬

Sistema web para la gestión integral de correspondencia institucional. Permite registrar, clasificar, auditar y exportar toda documentación que entra y sale del Centro de Estudios Regionales (CER).

## ¿Para qué sirve?

- **Registro centralizado**: Un solo lugar para toda la correspondencia
- **Traceabilidad completa**: Quién vio, cuándo, qué cambió, por qué
- **Código de barras automático**: Cada radicado obtiene uno único (Code128)
- **Reportes**: Exporta a PDF/Excel con un clic
- **Control de acceso**: 3 roles (Administrador, Operador, Consultor)

## Características principales

- ✅ Autenticación y control de roles de usuario
- ✅ Dashboard con resumen de radicados
- ✅ Registro y seguimiento de correspondencia
- ✅ Generación automática de códigos de barras
- ✅ Exportación a PDF y Excel
- ✅ Página de ayuda integrada
- ✅ Historial de cambios de estado
- ✅ Interfaz responsiva con Bootstrap 5

## Tecnologías utilizadas

| Tecnología          | Versión | Propósito                    |
| ------------------- | ------- | ---------------------------- |
| **Python**          | 3.9+    | Lenguaje principal           |
| **Django**          | 6.0.2   | Framework web                |
| **PostgreSQL**      | -       | Base de datos (configurable) |
| **SQLite**          | -       | Base de datos dev (default)  |
| **Bootstrap**       | 5.3+    | Framework CSS                |
| **ReportLab**       | 4.4.10  | Generación de PDFs           |
| **OpenPyXL**        | 3.1.5   | Generación de Excel          |
| **python-barcode**  | 0.16.1  | Códigos de barras            |
| **Pillow**          | 12.1.1  | Manipulación de imágenes     |
| **python-decouple** | 3.8     | Variables de entorno         |
| **WhiteNoise**      | 6.12.0  | Servir archivos estáticos    |

## Requisitos del sistema

- **Python**: 3.9 o superior
- **Base de datos**: PostgreSQL (producción) o SQLite (desarrollo)
- **Espacio en disco**: 500MB mínimo (para archivos subidos)
- **Memoria RAM**: 512MB mínimo

## Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd backend
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Seguridad
SECRET_KEY=tu-secret-key-muy-larga-y-aleatoria-aqui
DEBUG=True

# Base de datos (elige una opción)
# Opción 1: SQLite (desarrollo)
DB_ENGINE=django.db.backends.sqlite3

# Opción 2: PostgreSQL (producción)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=cer_correspondencia
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432

# Hosts permitidos
ALLOWED_HOSTS=127.0.0.1,localhost

# Configuración adicional (opcional)
LANGUAGE_CODE=es-co
TIME_ZONE=America/Bogota
```

**Nota**: Para generar una SECRET_KEY segura, ejecuta:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 5. Ejecutar migraciones

```bash
python manage.py migrate
```

### 6. Crear usuario administrador

```bash
python manage.py createsuperuser
```

Sigue las instrucciones para crear tu usuario admin.

### 7. Cargar datos iniciales (opcional)

```bash
python manage.py loaddata radicacion/migrations/initial_data.py
```

Esto carga tipos de correspondencia, estados y empresas básicas.

## Cómo ejecutar el servidor

### Desarrollo

```bash
python manage.py runserver
```

Accede en: http://localhost:8000

### Producción (con WhiteNoise)

```bash
# Preparar archivos estáticos
python manage.py collectstatic --no-input

# Ejecutar servidor
python manage.py runserver 0.0.0.0:8000
```

### Producción (con servidor web)

Para despliegue real, usa un servidor WSGI como Gunicorn:

```bash
pip install gunicorn
gunicorn backend.wsgi:application --bind 0.0.0.0:8000
```

## Estructura del proyecto

```
backend/
├── manage.py                 # Herramienta de línea de comandos de Django
├── db.sqlite3               # Base de datos SQLite (desarrollo)
├── requirements.txt         # Dependencias Python
├── README.md               # Esta documentación
├── passenger_wsgi.py       # Configuración para Passenger (servidores)
│
├── backend/                # Configuración principal de Django
│   ├── settings.py         # Configuración global
│   ├── urls.py             # Rutas raíz
│   ├── wsgi.py            # Interfaz WSGI
│   └── asgi.py            # Interfaz ASGI
│
├── radicacion/             # App principal
│   ├── models.py           # Modelos de datos
│   ├── views.py            # Lógica de vistas
│   ├── urls.py             # Rutas de la app
│   ├── admin.py            # Panel administrativo
│   ├── apps.py             # Configuración de la app
│   ├── services.py         # Servicios de negocio
│   ├── utils.py            # Utilidades
│   ├── permissions.py      # Gestión de permisos
│   ├── migrations/         # Migraciones de BD
│   ├── templates/          # Plantillas HTML
│   └── static/             # Archivos estáticos
│
├── media/                  # Archivos subidos por usuarios
│   ├── documentos/         # PDFs, Word, etc.
│   └── codigos/            # Códigos de barras generados
│
└── staticfiles/            # Archivos estáticos procesados
```

## Flujo de trabajo básico

1. **Usuario se registra** → Obtiene rol (consultor por defecto)
2. **Operador crea radicado** → Sistema genera número único + código de barras
3. **Cambios de estado** → Se registra en historial automáticamente
4. **Consultas y reportes** → Dashboard y exportaciones disponibles

## Roles y permisos

| Rol               | Ver radicados | Crear radicados | Cambiar estado | Exportar | Admin panel |
| ----------------- | ------------- | --------------- | -------------- | -------- | ----------- |
| **Consultor**     | ✅            | ❌              | ❌             | ✅       | ❌          |
| **Operador**      | ✅            | ✅              | ✅             | ✅       | ❌          |
| **Administrador** | ✅            | ✅              | ✅             | ✅       | ✅          |

## API y endpoints principales

- `/` - Dashboard principal
- `/radicados/` - Lista de radicados
- `/nuevo/` - Crear nuevo radicado
- `/exportar/pdf/` - Exportar a PDF
- `/exportar/excel/` - Exportar a Excel
- `/admin/` - Panel administrativo

## Solución de problemas comunes

### Error: "ModuleNotFoundError: No module named 'django'"

**Solución**: Asegúrate de activar el entorno virtual:

```bash
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

### Error: "Secret key not found"

**Solución**: Crea el archivo `.env` con la SECRET_KEY.

### Error: "Permission denied" al subir archivos

**Solución**: Verifica permisos de las carpetas `media/` y `staticfiles/`.

### Base de datos no se conecta

**Solución**: Verifica las variables de entorno en `.env` y que PostgreSQL esté corriendo.

## Desarrollo y contribución

### Ejecutar tests

```bash
python manage.py test
```

### Crear nueva migración

```bash
python manage.py makemigrations radicacion
python manage.py migrate
```

### Agregar nueva dependencia

1. Agrega al `requirements.txt`
2. Ejecuta `pip install -r requirements.txt`

## Despliegue

### Variables de entorno para producción

```env
DEBUG=False
SECRET_KEY=tu-secret-key-produccion
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
DB_ENGINE=django.db.backends.postgresql
# ... otras variables de BD
```

### Configuración de servidor web

Ejemplo con Nginx + Gunicorn:

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /media/ {
        alias /ruta/a/tu/proyecto/media/;
    }

    location /static/ {
        alias /ruta/a/tu/proyecto/staticfiles/;
    }
}
```

## Roadmap

- [ ] API REST completa
- [ ] Autenticación 2FA
- [ ] Notificaciones por email
- [ ] Búsqueda avanzada con Elasticsearch
- [ ] Integración LDAP corporativo
- [ ] Dashboard con gráficos interactivos

## Soporte

Para soporte técnico o reportar bugs:

- **Email**: soporte@cer.edu.co
- **Issues**: Abre un issue en el repositorio
- **Wiki**: Consulta la documentación interna

## Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## Autor

**Sebastián Páez** — [@SwbasAprende](https://github.com/SwbasAprende)

---

_Última actualización: Abril 2026_
