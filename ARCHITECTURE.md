# Arquitectura del Sistema de Correspondencia CER

## Visión general

Este documento explica la arquitectura del Sistema de Correspondencia del Centro de Estudios Regionales (CER), construido con Django 6.0. Este sistema permite gestionar, rastrear y auditar toda la correspondencia institucional.

## Arquitectura general

El sistema sigue el patrón **MVC (Model-View-Controller)** de Django, con capas adicionales para servicios de negocio y utilidades.

```
┌─────────────────────────────────────────────────────────────┐
│                    Navegador Web                            │
│  (Bootstrap 5 + JavaScript)                                 │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/HTTPS
┌─────────────────────▼───────────────────────────────────────┐
│                Django Framework                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              URL Dispatcher                         │    │
│  │  (urls.py) - Enruta URLs a vistas                   │    │
│  └─────────────────────┬───────────────────────────────┘    │
│                        │
│  ┌─────────────────────▼───────────────────────────────┐    │
│  │                Views (Controlador)                  │    │
│  │  (views.py) - Lógica de negocio, valida requests    │    │
│  └─────────────────────┬───────────────────────────────┘    │
│                        │
│  ┌─────────────────────▼───────────────────────────────┐    │
│  │              Services (Lógica de negocio)           │    │
│  │  (services.py, utils.py, permissions.py)            │    │
│  └─────────────────────┬───────────────────────────────┘    │
│                        │
│  ┌─────────────────────▼───────────────────────────────┐    │
│  │                Models (Datos)                       │    │
│  │  (models.py) - Estructura BD, validaciones          │    │
│  └─────────────────────┬───────────────────────────────┘    │
│                        │
│  ┌─────────────────────▼───────────────────────────────┐    │
│  │              Base de datos                          │    │
│  │  (PostgreSQL/SQLite) - Almacenamiento persistente   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Estructura de carpetas detallada

### Raíz del proyecto (`backend/`)

```
backend/
├── manage.py                 # CLI de Django - ejecutar comandos
├── db.sqlite3               # BD SQLite (desarrollo)
├── requirements.txt         # Dependencias Python
├── README.md               # Documentación principal
├── passenger_wsgi.py       # Configuración Passenger (servidores)
├── .env.example            # Ejemplo de variables entorno
└── backend/                # Configuración Django
    ├── __init__.py
    ├── settings.py         # Configuración global
    ├── urls.py             # URLs raíz
    ├── wsgi.py            # Interfaz servidor web
    └── asgi.py            # Interfaz ASGI (WebSockets)
```

### App principal (`radicacion/`)

```
radicacion/
├── __init__.py
├── models.py               # Modelos de datos
├── views.py                # Vistas (controladores)
├── urls.py                 # URLs de la app
├── admin.py                # Configuración admin Django
├── apps.py                 # Configuración de la app
├── services.py             # Servicios de negocio (exportación)
├── utils.py                # Utilidades (generación números)
├── permissions.py          # Gestión roles/permisos
│
├── migrations/             # Cambios en BD
│   ├── __init__.py
│   ├── 0001_initial.py    # Creación inicial tablas
│   └── ...                # Migraciones posteriores
│
├── templates/              # Plantillas HTML
│   └── radicacion/
│       ├── base.html       # Plantilla base (menú, layout)
│       ├── dashboard.html  # Página inicio
│       ├── lista.html      # Lista radicados
│       ├── crear.html      # Formulario crear
│       ├── detalle.html    # Detalle radicado
│       ├── sticker.html    # Etiqueta impresión
│       └── ayuda.html      # Página ayuda
│
└── static/                 # CSS, JS, imágenes
    └── radicacion/
        ├── css/            # Hojas estilo personalizadas
        └── js/             # JavaScript personalizado
```

### Archivos multimedia

```
media/                      # Archivos subidos usuarios
├── documentos/             # PDFs, Word radicados
└── codigos/               # Códigos barras generados

staticfiles/               # Archivos estáticos procesados
├── admin/                 # CSS/JS admin Django
├── radicacion/            # Archivos app
└── ...                    # Librerías (Bootstrap, etc.)
```

## Qué hace cada archivo importante

### Configuración

#### `backend/settings.py`

**Propósito**: Configuración global del proyecto Django.

**Contenido importante**:

- `INSTALLED_APPS`: Apps activas (django.contrib.\*, radicacion)
- `DATABASES`: Configuración BD (SQLite/PostgreSQL)
- `MIDDLEWARE`: Capas procesamiento requests
- `TEMPLATES`: Configuración plantillas HTML
- `STATIC_URL/MEDIA_URL`: URLs archivos estáticos/subidos
- `AUTH_*`: Configuración autenticación

#### `backend/urls.py`

**Propósito**: Rutas URL raíz del proyecto.

**Contenido**:

- `/admin/` → Panel administrativo Django
- `/accounts/login|logout/` → Autenticación
- `/` → App radicacion (include radicacion.urls)

### Modelos de datos

#### `radicacion/models.py`

**Propósito**: Define estructura base de datos y lógica datos.

**Modelos principales**:

- `EstadoRadicado`: Estados posibles (Recibido, Procesado, etc.)
- `TipoCorrespondencia`: Categorías (Oficio, Factura, etc.)
- `Empresa`: Instituciones (CER, otras)
- `Radicado`: Documento principal con metadata
- `Perfil`: Roles usuarios (Admin, Operador, Consultor)
- `HistorialEstado`: Auditoría cambios estado

**Lógica importante**:

- Generación automática números radicado
- Creación códigos barras al guardar
- Validaciones campos

### Vistas y controladores

#### `radicacion/views.py`

**Propósito**: Maneja requests HTTP, coordina lógica negocio.

**Vistas principales**:

- `dashboard()`: Estadísticas generales
- `lista_radicados()`: Lista con filtros búsqueda
- `crear_radicado()`: Formulario creación
- `detalle_radicado()`: Vista detalle + historial
- `cambiar_estado()`: Cambiar estado radicado
- `exportar_pdf/excel()`: Generar reportes

**Patrón**: Cada vista maneja un endpoint, valida permisos, llama servicios.

### Servicios de negocio

#### `radicacion/services.py`

**Propósito**: Lógica negocio reutilizable.

**Servicios**:

- `ExportadorRadicados`: Genera PDFs/Excel radicados

#### `radicacion/utils.py`

**Propósito**: Utilidades generales.

**Utilidades**:

- `GeneradorNumerosRadicado`: Crea números únicos radicados

#### `radicacion/permissions.py`

**Propósito**: Gestión permisos y roles.

**Funciones**:

- `obtener_rol()`: Rol del usuario
- `puede_*()`: Verificar permisos específicos

### URLs y enrutamiento

#### `radicacion/urls.py`

**Propósito**: Conecta URLs con vistas.

**Rutas principales**:

- `''` → dashboard
- `'radicados/'` → lista_radicados
- `'nuevo/'` → crear_radicado
- `'<int:pk>/'` → detalle_radicado
- `'exportar/pdf/'` → exportar_pdf

## Flujo de datos: De request a response

### Ejemplo: Crear un radicado

```
1. Usuario envía POST /nuevo/
   ↓
2. Django URL dispatcher
   - Busca patrón en urls.py
   - Encuentra: path('nuevo/', crear_radicado)
   ↓
3. Vista crear_radicado()
   - Valida usuario autenticado
   - Verifica permisos (GestorRoles.puede_crear_radicado)
   - Extrae datos del request.POST
   ↓
4. Creación del objeto Radicado
   - Radicado.objects.create(...)
   ↓
5. Método save() del modelo
   - Genera número único (GeneradorNumerosRadicado.generar)
   - Guarda en BD
   - Genera código barras (_generar_codigo_barras)
   ↓
6. Registro en historial
   - HistorialEstado.objects.create(estado_nuevo=...)
   ↓
7. Respuesta al usuario
   - redirect('/detalle/{id}/')
   ↓
8. Usuario ve página detalle
```

### Ejemplo: Exportar a PDF

```
1. Usuario hace GET /exportar/pdf/
   ↓
2. URL dispatcher → exportar_pdf()
   ↓
3. Vista exportar_pdf()
   - Llama ExportadorRadicados.exportar_a_pdf()
   ↓
4. Servicio exportar_a_pdf()
   - Consulta BD: Radicado.objects.all().order_by('-fecha')
   - Construye tabla PDF con ReportLab
   - Retorna HttpResponse con PDF
   ↓
5. Usuario descarga archivo
```

## Decisiones arquitectónicas clave

### 1. Separación de responsabilidades

**Decisión**: Lógica negocio en servicios separados (services.py, utils.py, permissions.py)

**Razones**:

- Views delgadas, fáciles testear
- Reutilización código
- Mantenimiento más simple

### 2. Generación automática de números

**Decisión**: Números radicado generados automáticamente en modelo

**Formato**: `{EMPRESA}-{TIPO}-{FECHA}-{CONSECUTIVO}`
**Ejemplo**: `CER-DOC-20260415-0001`

**Razones**:

- Unicidad garantizada
- Auditable (fecha, tipo, empresa en el número)
- No error humano

### 3. Historial de cambios

**Decisión**: Tabla separada `HistorialEstado` para auditoría

**Razones**:

- Traceabilidad completa
- Performance (Radicado no crece indefinidamente)
- Compliance normativo

### 4. Roles simples

**Decisión**: 3 roles fijos (Admin, Operador, Consultor)

**Razones**:

- Suficiente para necesidades actuales
- Simple implementar y mantener
- Extensible si crecen requerimientos

## Base de datos

### Esquema principal

```
EstadoRadicado
├── id (PK)
├── nombre (VARCHAR)

TipoCorrespondencia
├── id (PK)
├── nombre (VARCHAR)
└── codigo (VARCHAR, UNIQUE)

Empresa
├── id (PK)
├── nombre (VARCHAR)
└── codigo (VARCHAR, UNIQUE)

User (Django auth)
├── id (PK)
├── username (VARCHAR)
├── email (VARCHAR)
└── ... otros campos Django

Perfil
├── id (PK)
├── user_id (FK → User)
└── rol (VARCHAR: administrador|operador|consultor)

Radicado
├── id (PK)
├── numero (VARCHAR, UNIQUE)
├── fecha (DATETIME)
├── remitente (VARCHAR)
├── destinatario (VARCHAR, NULL)
├── asunto (TEXT)
├── direccion (VARCHAR: recibido|enviado)
├── documento (FILE, NULL)
├── codigo_barras (IMAGE, NULL)
├── tipo_id (FK → TipoCorrespondencia)
├── estado_id (FK → EstadoRadicado)
├── usuario_id (FK → User)
└── empresa_id (FK → Empresa, NULL)

HistorialEstado
├── id (PK)
├── radicado_id (FK → Radicado)
├── estado_anterior_id (FK → EstadoRadicado, NULL)
├── estado_nuevo_id (FK → EstadoRadicado)
├── usuario_id (FK → User)
├── fecha (DATETIME)
└── observacion (TEXT, NULL)
```

### Índices importantes

- `Radicado.numero` (UNIQUE)
- `Radicado.fecha` (para ordenamiento)
- `HistorialEstado.fecha` (ordenamiento descendente)
- `HistorialEstado.radicado_id` (FK)

## Seguridad

### Autenticación

- Django auth nativo
- Sesiones seguras
- Protección CSRF

### Autorización

- Decorador `@login_required`
- Verificación roles por vista
- Permisos granulares por acción

### Datos sensibles

- SECRET_KEY en variables entorno
- Contraseñas hasheadas
- Validación inputs

## Despliegue

### Desarrollo

```bash
python manage.py runserver
```

### Producción

- WhiteNoise para archivos estáticos
- PostgreSQL para BD
- Gunicorn + Nginx recomendados
- Variables entorno obligatorias

## Testing

### Estrategia

- Tests unitarios para servicios
- Tests integración para views
- Tests BD para modelos

### Ejecución

```bash
python manage.py test
```

## Mantenimiento

### Tareas comunes

- `python manage.py migrate` - Aplicar cambios BD
- `python manage.py collectstatic` - Preparar archivos estáticos
- `python manage.py createsuperuser` - Crear admin

### Monitoreo

- Logs Django
- Queries BD lentas
- Uso disco (archivos subidos)

---

_Este documento debe mantenerse actualizado con cambios en la arquitectura._
