import sys
import os

# Apunta al directorio raíz del proyecto
INTERP = os.path.join(os.environ['HOME'], 'virtualenv', 'correspondencia', 'bin', 'python')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Agrega el proyecto al path de Python
sys.path.insert(0, os.getcwd())

# Indica a Django qué settings usar
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'

# Importa la aplicación WSGI de Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
