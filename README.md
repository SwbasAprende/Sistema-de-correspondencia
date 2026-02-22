# Sistema de Correspondencia 📬

Sistema web para la gestión y radicación de correspondencia institucional.

## Características

- Autenticación y control de roles de usuario
- Dashboard con resumen de radicados
- Registro y seguimiento de correspondencia
- Generación de códigos de barras
- Exportación a PDF y Excel
- Página de ayuda integrada

## Tecnologías utilizadas

- Python / Django
- SQLite
- Bootstrap 5 + Bootstrap Icons
- ReportLab (PDF)
- OpenPyXL (Excel)
- python-barcode + Pillow

## Instalación

1. Clona el repositorio
2. Crea y activa un entorno virtual
3. Instala las dependencias
4. Configura el archivo .env
5. Ejecuta las migraciones
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Configuración

Crea un archivo `.env` en la raíz del proyecto con:
```
SECRET_KEY=tu_secret_key_aqui
```

## Autor

Sebastián Páez — [@SwbasAprende](https://github.com/SwbasAprende)