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
    codigo = models.CharField(max_length=10, unique=True, default='DOC')
    def __str__(self):
        return F"{self.nombre} ({self.codigo})"

class Empresa(models.Model):
    nombre = models.CharField(max_length=150)
    codigo = models.CharField(max_length=10, unique=True)
    def __str__(self):
        return F"{self.nombre} ({self.codigo})"
        

class Radicado(models.Model):
    DIRECCION_CHOICES = [
        ('recibido', 'Correo Recibido'),
        ('enviado', 'Correo Enviado'),
    ]

    numero = models.CharField(max_length=50, unique=True, blank=True)
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
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, null=True, blank=True, help_text="CER")

    def _generar_numero(self):
        ahora = timezone.now()
        fecha_str = ahora.strftime('%Y%m%d')

        codigo_empresa = self.empresa.codigo if self.empresa else 'CER'

        codigo_tipo = self.tipo.codigo if self.tipo else 'DOC'

        prefijo = f"{codigo_empresa}-{codigo_tipo}-{fecha_str}-"
        ultimo = (
            Radicado.objects
            .filter(numero__startswith=prefijo)
            .order_by('id')
            .last()
        )

        if not ultimo:
            consecutivo = 1
        else:
            try:
                consecutivo = int(ultimo.numero.rsplit('-', 1)[-1]) + 1
            except (ValueError, IndexError):
                consecutivo = Radicado.objects.filter(numero__startswith=prefijo).count() + 1

        return f"{prefijo}{consecutivo:04d}"

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self._generar_numero()

        if not self.codigo_barras:
            codigo = barcode.get('code128', self.numero, writer=ImageWriter())
            buffer = BytesIO()
            codigo.write(buffer)
            self.codigo_barras.save(f'barcode_{self.numero}.png', File(buffer), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_direccion_display()} - {self.numero}"

class Perfil(models.Model):
    ROL_CHOICES = [ 
        ('administrador', 'Administrador'),
        ('operador', 'Operador'),
        ('consultor', 'Consultor')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='consultor')

class HistorialEstado(models.Model):
    """
    Registra cada cambio de estado de un radicado:
    quién lo cambió, cuándo, desde qué estado y hacia cuál.
    """
    radicado = models.ForeignKey(
        Radicado,
        on_delete=models.CASCADE,
        related_name='historial'
    )
    estado_anterior = models.ForeignKey(
        EstadoRadicado,
        on_delete=models.PROTECT,
        related_name='historial_anterior',
        null=True,
        blank=True
    )
    estado_nuevo = models.ForeignKey(
        EstadoRadicado,
        on_delete=models.PROTECT,
        related_name='historial_nuevo'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )
    fecha = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.radicado.numero} → {self.estado_nuevo} ({self.fecha:%d/%m/%Y %H:%M})"