from django.contrib import admin
from .models import Radicado, EstadoRadicado, TipoCorrespondencia, Perfil
from .models import Empresa

admin.site.register(Empresa)
admin.site.register(Radicado)
admin.site.register(EstadoRadicado)
admin.site.register(TipoCorrespondencia)
admin.site.register(Perfil)