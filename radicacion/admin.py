from django.contrib import admin
from .models import Radicado, EstadoRadicado, TipoCorrespondencia, Perfil

admin.site.register(Radicado)
admin.site.register(EstadoRadicado)
admin.site.register(TipoCorrespondencia)
admin.site.register(Perfil)