from django.contrib import admin

from .models import Empresa, EstadoRadicado, Perfil, Radicado, TipoCorrespondencia

admin.site.register(Empresa)
admin.site.register(Radicado)
admin.site.register(EstadoRadicado)
admin.site.register(TipoCorrespondencia)
admin.site.register(Perfil)