from django.db import models
from django.contrib.auth.models import User
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
from django.utils import timezone

class EstadoRadicado(models.Model):
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre

class TipoCorrespondencia(models.Model):
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre

class Radicado(models.Model):
    DIRECCION_CHOICES = [
        ('recibido', 'Correo Recibido'),
        ('enviado', 'Correo Enviado'),
    ]

    numero = models.CharField(max_length=30, unique=True, blank=True)
    fecha = models.DateField(auto_now_add=True)
    remitente = models.CharField(max_length=150)
    destinatario = models.CharField(max_length=150, blank=True, null=True)
    asunto = models.TextField()
    direccion = models.CharField(max_length=10, choices=DIRECCION_CHOICES, default='recibido')
    documento = models.FileField(upload_to='documentos/', blank=True, null=True)
    codigo_barras = models.ImageField(upload_to='codigos/', blank=True, null=True)

    tipo = models.ForeignKey(TipoCorrespondencia, on_delete=models.PROTECT)
    estado = models.ForeignKey(EstadoRadicado, on_delete=models.PROTECT)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        if not self.numero:
            anio_actual = timezone.now().year
            ultimo = Radicado.objects.filter(numero__startswith=str(anio_actual)).order_by('id').last()
            if not ultimo:
                nuevo_consecutivo = 1
            else:
                try:
                    ultimo_num = int(ultimo.numero.split('-')[1])
                    nuevo_consecutivo = ultimo_num + 1
                except:
                    nuevo_consecutivo = Radicado.objects.count() + 1
            self.numero = f"{anio_actual}-{nuevo_consecutivo:04d}"

        if not self.codigo_barras:
            codigo = barcode.get('code128', self.numero, writer=ImageWriter())
            buffer = BytesIO()
            codigo.write(buffer)
            self.codigo_barras.save(f'barcode_{self.numero}.png', File(buffer), save=False)
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_direccion_display()} - {self.numero}"

class Perfil(models.Model):
    ROL_CHOICES = [('administrador', 'Administrador'), ('operador', 'Operador'), ('consultor', 'Consultor')]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='consultor')