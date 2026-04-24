# DOCUMENTACIÓN TÉCNICA COMPLETA

## Sistema de Correspondencia Institucional del CER

**Proyecto:** Sistema de Correspondencia Institucional del CER (Corporación Centro de Estudios Regionales), Magdalena Medio, Colombia.  
**Desarrollado en:** Django + PostgreSQL (Supabase).  
**Desplegado en:** Render.com.  
**Cumple con:** Ley 594 de 2000 de Colombia (gestión documental).  
**Autor:** Sebastián Páez (@SwbasAprende). Abril 2026.

---

## 1. Visión General del Proyecto

### ¿Qué hace el sistema?

El Sistema de Correspondencia Institucional del CER es una aplicación web desarrollada en Django que permite gestionar, rastrear y auditar toda la correspondencia que entra y sale del Centro de Estudios Regionales. El sistema automatiza el proceso de radicación documental, generando números únicos, códigos de barras y manteniendo un historial completo de cambios para cumplimiento normativo.

### Problema que resuelve

- **Gestión manual ineficiente**: Antes, la correspondencia se manejaba en papel con registros dispersos y difíciles de consultar.
- **Falta de trazabilidad**: No había forma de saber quién modificó qué documento ni cuándo.
- **Errores humanos**: Numeración manual propensa a duplicados o inconsistencias.
- **Ausencia de auditoría**: Sin historial de cambios, era imposible verificar el cumplimiento de la Ley 594 de 2000.
- **Dificultad en reportes**: Generar estadísticas o exportar datos requería trabajo manual tedioso.

### Usuarios objetivo

- **Consultores**: Pueden ver radicados, exportar reportes y consultar el sistema de forma read-only.
- **Operadores**: Además de consultar, pueden crear nuevos radicados y cambiar estados de los documentos.
- **Administradores**: Tienen acceso completo, incluyendo el panel administrativo de Django para gestión de usuarios, tipos de correspondencia y estados.

---

## 2. Stack Tecnológico

| Tecnología          | Versión | Propósito en el proyecto                            |
| ------------------- | ------- | --------------------------------------------------- |
| **Python**          | 3.9+    | Lenguaje principal para desarrollo backend          |
| **Django**          | 6.0.2   | Framework web MVC para estructura de la aplicación  |
| **PostgreSQL**      | -       | Base de datos relacional para producción (Supabase) |
| **SQLite**          | -       | Base de datos para desarrollo local                 |
| **Bootstrap**       | 5.3+    | Framework CSS para interfaz responsiva              |
| **ReportLab**       | 4.4.10  | Generación de documentos PDF con tablas y estilos   |
| **OpenPyXL**        | 3.1.5   | Creación de archivos Excel con formato y colores    |
| **python-barcode**  | 0.16.1  | Generación de códigos de barras Code128             |
| **Pillow**          | 12.1.1  | Procesamiento de imágenes (códigos de barras PNG)   |
| **python-decouple** | 3.8     | Gestión de variables de entorno seguras             |
| **WhiteNoise**      | 6.12.0  | Servidor de archivos estáticos en producción        |
| **asgiref**         | 3.11.1  | Soporte ASGI para Django moderno                    |
| **sqlparse**        | 0.5.5   | Parseo de SQL para debugging de queries             |
| **tzdata**          | 2025.3  | Zonas horarias (America/Bogota configurada)         |

Cada tecnología fue elegida por su madurez, compatibilidad con Django y capacidad para resolver necesidades específicas del proyecto.

---

## 3. Arquitectura del Proyecto

### Estructura de carpetas

```
backend/
├── manage.py                 # CLI de Django para comandos
├── db.sqlite3               # BD SQLite (desarrollo)
├── requirements.txt         # Dependencias Python
├── README.md               # Documentación usuario
├── ARCHITECTURE.md         # Documentación técnica
├── passenger_wsgi.py       # Configuración Passenger
├── .env.example            # Variables entorno ejemplo
├── .env                    # Variables entorno (no versionado)
├── backend/                # Configuración Django
│   ├── settings.py         # Configuración global
│   ├── urls.py             # URLs raíz
│   ├── wsgi.py             # Interfaz WSGI
│   └── asgi.py             # Interfaz ASGI
├── radicacion/             # App principal
│   ├── models.py           # Modelos de datos
│   ├── views.py            # Lógica de vistas
│   ├── urls.py             # URLs de la app
│   ├── admin.py            # Panel admin Django
│   ├── apps.py             # Configuración app
│   ├── services.py         # Servicios negocio
│   ├── utils.py            # Utilidades
│   ├── permissions.py      # Gestión permisos
│   ├── tests.py            # Tests (vacío)
│   ├── migrations/         # Cambios BD
│   ├── templates/          # Plantillas HTML
│   └── static/             # CSS/JS personalizados
├── media/                  # Archivos subidos
│   ├── documentos/         # PDFs/Word radicados
│   └── codigos/           # Códigos barras PNG
└── staticfiles/           # Estáticos procesados
```

### Patrón de diseño

El proyecto sigue el patrón **MTV (Model-Template-View)** de Django, con capas adicionales:

- **Modelos**: Representan datos y lógica de negocio
- **Vistas**: Manejan requests HTTP y coordinan respuestas
- **Templates**: Capa de presentación HTML
- **Servicios**: Lógica de negocio reutilizable (exportaciones)
- **Utilidades**: Funciones auxiliares (generación números)
- **Permisos**: Gestión de roles y autorizaciones

### Diagrama de flujo general

```
Usuario → Request HTTP → URL Dispatcher → Vista → Servicios/Utilidades → Modelo → Base de Datos
    ↓
Respuesta ← Template ← Vista ← Servicios ← Modelo ← Resultados Query
```

---

## 4. Módulos y Aplicaciones Django

### App principal: radicacion

#### Propósito

La app `radicacion` contiene toda la lógica de negocio del sistema de correspondencia. Maneja la creación, consulta, modificación y exportación de radicados documentales.

#### Modelos

| Modelo              | Campos principales                                                                                                          | Relaciones                                              |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| EstadoRadicado      | id, nombre                                                                                                                  | -                                                       |
| TipoCorrespondencia | id, nombre, codigo (único)                                                                                                  | -                                                       |
| Empresa             | id, nombre, codigo (único)                                                                                                  | -                                                       |
| Radicado            | numero (único), fecha, remitente, destinatario, asunto, direccion, documento, codigo_barras, tipo, estado, usuario, empresa | FK a TipoCorrespondencia, EstadoRadicado, User, Empresa |
| Perfil              | id, user, rol                                                                                                               | OneToOne con User                                       |
| HistorialEstado     | radicado, estado_anterior, estado_nuevo, usuario, fecha, observacion                                                        | FK a Radicado, EstadoRadicado x2, User                  |

#### Vistas principales

| Vista            | Método   | URL                   | Descripción                        |
| ---------------- | -------- | --------------------- | ---------------------------------- |
| dashboard        | GET      | /                     | Estadísticas generales del sistema |
| lista_radicados  | GET      | /radicados/           | Lista con filtros de búsqueda      |
| crear_radicado   | GET/POST | /nuevo/               | Formulario creación radicado       |
| detalle_radicado | GET      | /<pk>/                | Detalle radicado + historial       |
| cambiar_estado   | POST     | /<pk>/cambiar-estado/ | Cambiar estado radicado            |
| imprimir_sticker | GET      | /<pk>/imprimir/       | Página optimizada impresión        |
| barcode_image    | GET      | /<pk>/barcode/        | Servir imagen código barras        |
| exportar_pdf     | GET      | /exportar/pdf/        | Exportar radicados a PDF           |
| exportar_excel   | GET      | /exportar/excel/      | Exportar radicados a Excel         |
| ayuda            | GET      | /ayuda/               | Página ayuda contextual            |

#### URLs expuestas

- `/` - Dashboard
- `/radicados/` - Lista radicados
- `/nuevo/` - Crear radicado
- `/<int:pk>/` - Detalle radicado
- `/<int:pk>/cambiar-estado/` - Cambiar estado
- `/<int:pk>/barcode/` - Imagen código barras
- `/<int:pk>/imprimir/` - Sticker impresión
- `/exportar/pdf/` - Exportar PDF
- `/exportar/excel/` - Exportar Excel
- `/ayuda/` - Ayuda

#### Formularios

No utiliza Django Forms. Los formularios se manejan directamente en templates HTML con inputs nativos y validación manual en vistas.

---

## 5. Base de Datos

### Diagrama entidad-relación (descrito)

```
EstadoRadicado
├── id (PK)
└── nombre

TipoCorrespondencia
├── id (PK)
├── nombre
└── codigo (UNIQUE)

Empresa
├── id (PK)
├── nombre
└── codigo (UNIQUE)

User (Django auth)
├── id (PK)
├── username
├── email
└── otros campos Django

Perfil
├── id (PK)
├── user_id (FK → User, OneToOne)
└── rol (choices: administrador/operador/consultor)

Radicado
├── id (PK)
├── numero (VARCHAR, UNIQUE)
├── fecha (DATETIME, auto_now_add)
├── remitente (VARCHAR)
├── destinatario (VARCHAR, NULL)
├── asunto (TEXT)
├── direccion (VARCHAR: recibido/enviado)
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
├── fecha (DATETIME, auto_now_add)
└── observacion (TEXT, NULL)
```

### Tablas principales y relaciones

- **Radicado** es la tabla central, relacionada con todas las demás
- **HistorialEstado** registra cambios de estado para auditoría
- **Perfil** extiende User con roles de acceso
- Relaciones ForeignKey con on_delete=PROTECT evitan borrado accidental

### Campos importantes

- `Radicado.numero`: Identificador único generado automáticamente
- `Radicado.fecha`: Timestamp creación
- `HistorialEstado.fecha`: Timestamp cambios (ordenado DESC)
- `Perfil.rol`: Controla permisos de acceso

---

## 6. Funcionalidades Principales

### 1. Dashboard

**Qué hace:** Muestra estadísticas generales del sistema.  
**Módulos:** views.py (dashboard), templates/dashboard.html.  
**Resultado:** Página con totales, distribución por estado, últimos radicados.

### 2. Lista de Radicados

**Qué hace:** Lista todos los radicados con filtros de búsqueda.  
**Módulos:** views.py (lista_radicados), templates/lista.html.  
**Resultado:** Tabla paginada con filtros por texto y dirección.

### 3. Crear Radicado

**Qué hace:** Permite crear nuevo radicado con formulario.  
**Módulos:** views.py (crear_radicado), models.py (save), utils.py (generar número).  
**Resultado:** Nuevo radicado con número único y código barras generado.

### 4. Detalle de Radicado

**Qué hace:** Muestra información completa + historial de cambios.  
**Módulos:** views.py (detalle_radicado), templates/detalle.html.  
**Resultado:** Página con datos radicado y timeline de estados.

### 5. Cambiar Estado

**Qué hace:** Modifica estado del radicado y registra cambio.  
**Módulos:** views.py (cambiar_estado), models.py (HistorialEstado).  
**Resultado:** Estado actualizado + entrada en historial.

### 6. Generar Código Barras

**Qué hace:** Crea imagen Code128 automáticamente.  
**Módulos:** models.py (\_generar_codigo_barras), python-barcode.  
**Resultado:** Archivo PNG en media/codigos/.

### 7. Exportar a PDF

**Qué hace:** Genera reporte PDF con tabla de radicados.  
**Módulos:** services.py (ExportadorRadicados), ReportLab.  
**Resultado:** Archivo PDF descargable con formato profesional.

### 8. Exportar a Excel

**Qué hace:** Crea archivo Excel con datos de radicados.  
**Módulos:** services.py (ExportadorRadicados), OpenPyXL.  
**Resultado:** Archivo XLSX con estilos y formato.

### 9. Sistema de Roles

**Qué hace:** Controla permisos basado en roles de usuario.  
**Módulos:** permissions.py (GestorRoles), models.py (Perfil).  
**Resultado:** Acceso restringido según rol (admin/operador/consultor).

---

## 7. Configuración y Variables de Entorno

### Variables requeridas en .env

| Variable      | Requerida   | Descripción                     | Ejemplo                           |
| ------------- | ----------- | ------------------------------- | --------------------------------- |
| SECRET_KEY    | Sí          | Clave secreta Django            | django-insecure-abc123...         |
| DEBUG         | Sí          | Modo desarrollo (False en prod) | False                             |
| ALLOWED_HOSTS | Sí          | Hosts permitidos                | 127.0.0.1,localhost,midominio.com |
| DB_ENGINE     | Sí          | Motor BD                        | django.db.backends.postgresql     |
| DB_NAME       | Condicional | Nombre BD (si no SQLite)        | cer_correspondencia               |
| DB_USER       | Condicional | Usuario BD                      | miusuario                         |
| DB_PASSWORD   | Condicional | Password BD                     | mipassword                        |
| DB_HOST       | Condicional | Host BD                         | localhost                         |
| DB_PORT       | Condicional | Puerto BD                       | 5432                              |

### Configuraciones importantes en settings.py

- **INSTALLED_APPS**: Incluye 'radicacion' y apps Django estándar
- **MIDDLEWARE**: Incluye WhiteNoise para estáticos en producción
- **DATABASES**: Configurable entre SQLite (dev) y PostgreSQL (prod)
- **TEMPLATES**: Busca templates en app dirs
- **STATICFILES_STORAGE**: WhiteNoise en producción
- **MEDIA_URL/MEDIA_ROOT**: Configuración archivos subidos
- **AUTH_PASSWORD_VALIDATORS**: Validadores de contraseña estándar
- **LANGUAGE_CODE**: 'es-co' (español Colombia)
- **TIME_ZONE**: 'America/Bogota'

### Diferencias desarrollo vs producción

| Aspecto            | Desarrollo        | Producción              |
| ------------------ | ----------------- | ----------------------- |
| DEBUG              | True              | False                   |
| ALLOWED_HOSTS      | localhost         | Dominio real            |
| Base de datos      | SQLite            | PostgreSQL              |
| Archivos estáticos | Django dev server | WhiteNoise              |
| SECRET_KEY         | En .env           | Variable entorno segura |
| Logging            | Consola           | Archivo/logs            |

---

## 8. Flujos de Usuario

### Flujo de Consultor

1. **Login**: Usuario ingresa credenciales
2. **Dashboard**: Ve estadísticas generales (totales, distribución)
3. **Lista radicados**: Puede filtrar y buscar radicados existentes
4. **Ver detalle**: Consulta información completa de cualquier radicado
5. **Exportar**: Puede descargar PDF o Excel de todos los radicados
6. **Ayuda**: Accede a documentación del sistema

### Flujo de Operador

1. **Login**: Usuario con rol operador
2. **Todas las funciones de consultor** +
3. **Crear radicado**: Llena formulario y sube documento opcional
4. **Cambiar estado**: Modifica estado de radicados existentes
5. **Ver códigos barras**: Accede a imágenes generadas

### Flujo de Administrador

1. **Login**: Usuario con rol administrador
2. **Todas las funciones de operador** +
3. **Panel admin**: Accede a /admin/ para gestionar usuarios, tipos, estados
4. **Gestión usuarios**: Crear/modificar usuarios y asignar roles

### Flujo de creación de radicado

1. Usuario operador hace clic "Nuevo radicado"
2. Sistema valida permisos (GestorRoles.puede_crear_radicado)
3. Muestra formulario con selects precargados
4. Usuario llena campos y opcionalmente sube archivo
5. Al enviar POST, sistema:
   - Crea instancia Radicado
   - Genera número único (GeneradorNumerosRadicado)
   - Guarda en BD
   - Genera código barras (python-barcode + Pillow)
   - Crea entrada inicial en HistorialEstado
6. Redirige a página detalle del radicado creado

### Flujo de cambio de estado

1. En página detalle, operador selecciona nuevo estado
2. Agrega observación opcional
3. Envía formulario POST
4. Sistema valida que estado cambió realmente
5. Actualiza Radicado.estado
6. Crea nueva entrada en HistorialEstado
7. Recarga página detalle con historial actualizado

---

Documento generado el 16 de abril de 2026 analizando todo el código del proyecto CER</content>
<parameter name="filePath">c:\Users\USUARIO\Documents\correspondencia\backend\DOCUMENTACION_TECNICA.md
