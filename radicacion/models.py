from django.db import models
from django.contrib.auth.models import User
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
from django.utils import timezone

from .utils import GeneradorNumerosRadicado

class EstadoRadicado(models.Model):
    """
    Representa el estado actual de un radicado.
    
    Estados típicos: 'Recibido', 'En proceso', 'Archivado', 'Rechazado'.
    Cada radicado tiene exactamente un estado en cada momento.
    """
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre

class TipoCorrespondencia(models.Model):
    """
    Categoriza el tipo de correspondencia.
    
    Ejemplos: 'Oficio', 'Factura', 'Contrato'.
    Cada tipo tiene un código único (ej: 'OFI', 'FAC').
    """
    nombre = models.CharField(max_length=50)
    codigo = models.CharField(max_length=10, unique=True, default='DOC')
    def __str__(self):
        return F"{self.nombre} ({self.codigo})"

class Empresa(models.Model):
    """
    Institución o empresa responsable del radicado.
    
    Default: Centro de Estudios Regionales (CER).
    Cada radicado pertenece a una empresa.
    """
    nombre = models.CharField(max_length=150)
    codigo = models.CharField(max_length=10, unique=True)
    def __str__(self):
        return F"{self.nombre} ({self.codigo})"
        

class Radicado(models.Model):
    """
    Representa un documento de correspondencia registrado en el sistema.
    
    Cada radicado recibe un número único generado automáticamente con formato:
    EMPRESA-TIPO-FECHA-CONSECUTIVO (ej: CER-DOC-20260415-0001)
    
    Un radicado puede ser:
    - Correo Recibido: enviado a la institución desde afuera
    - Correo Enviado: creado por la institución para enviar afuera
    
    El HistorialEstado registra toda transición de estado para auditoría.
    """
    DIRECCION_CHOICES = [
        ('recibido', 'Correo Recibido'),
        ('enviado', 'Correo Enviado'),
    ]

    numero = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text="Auto-generado en formato: EMPRESA-TIPO-FECHA-CONSECUTIVO"
    )
    fecha = models.DateTimeField(auto_now_add=True)
    remitente = models.CharField(max_length=150)
    destinatario = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Opcional si es correo recibido"
    )
    asunto = models.TextField()
    direccion = models.CharField(max_length=10, choices=DIRECCION_CHOICES, default='recibido')
    documento = models.FileField(
        upload_to='documentos/',
        blank=True,
        null=True,
        help_text="PDF, Word, etc. - Opcional"
    )
    codigo_barras = models.ImageField(upload_to='codigos/', blank=True, null=True)

    tipo = models.ForeignKey(TipoCorrespondencia, on_delete=models.PROTECT)
    estado = models.ForeignKey(EstadoRadicado, on_delete=models.PROTECT)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="Centro de Estudios Regionales (CER) - Dejar vacío para default"
    )

    def save(self, *args, **kwargs):
        """
        Guarda el radicado en la base de datos.

        Lógica especial:
        - Si no tiene número, genera uno automáticamente usando GeneradorNumerosRadicado
        - Después de guardar, genera el código de barras si no existe
        """
        # Generar número único solo si es un radicado nuevo sin número asignado
        if not self.numero:
            self.numero = GeneradorNumerosRadicado.generar(self.empresa, self.tipo)

        # Guardar primero para obtener el ID y poder generar el código de barras
        super().save(*args, **kwargs)

        # Generar código de barras después de guardar (necesita self.numero)
        if not self.codigo_barras:
            self._generar_codigo_barras()

    def _generar_codigo_barras(self):
        """
        Genera y guarda la imagen del código de barras para este radicado.

        Usa el formato Code128 con el número del radicado.
        La imagen se guarda en media/codigos/ con nombre barcode_{numero}.png
        """
        # Crear código de barras Code128 con el número del radicado
        codigo = barcode.get('code128', self.numero, writer=ImageWriter())

        # Generar imagen en memoria (no guardar archivo temporal)
        buffer = BytesIO()
        codigo.write(buffer)
        buffer.seek(0)

        # Guardar imagen en el campo codigo_barras del modelo
        self.codigo_barras.save(f'barcode_{self.numero}.png', File(buffer))

    def __str__(self):
        """
        Representación string del radicado.

        Formato: "Dirección - Número"
        Ejemplo: "Correo Recibido - CER-DOC-20260415-0001"
        """
        return f"{self.get_direccion_display()} - {self.numero}"

class Perfil(models.Model):
    """
    Extiende el modelo User de Django con roles de acceso.

    Roles disponibles:
    - Administrador: acceso completo al sistema
    - Operador: puede crear radicados y cambiar estados
    - Consultor: solo lectura y exportación (rol por defecto)
    """
    ROL_CHOICES = [
        ('administrador', 'Administrador'),
        ('operador', 'Operador'),
        ('consultor', 'Consultor')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='consultor')

    def __str__(self):
        """Representación: 'username - Rol'"""
        return f"{self.user.username} - {self.get_rol_display()}"

class HistorialEstado(models.Model):
    """
    Registra cada cambio de estado de un radicado para auditoría completa.

    Cada vez que un radicado cambia de estado, se crea un registro aquí.
    Esto permite rastrear quién cambió qué, cuándo y por qué.

    Campos importantes:
    - estado_anterior: NULL para el primer registro (creación del radicado)
    - estado_nuevo: Estado al que cambió
    - observacion: Comentarios opcionales del cambio
    """
    # Relación con el radicado que cambió
    radicado = models.ForeignKey(
        Radicado,
        on_delete=models.CASCADE,  # Si borra radicado, borra historial
        related_name='historial'   # Acceso: radicado.historial.all()
    )

    # Estado antes del cambio (NULL si es creación)
    estado_anterior = models.ForeignKey(
        EstadoRadicado,
        on_delete=models.PROTECT,  # No borrar si hay historial
        related_name='historial_anterior',
        null=True,                # NULL para creación inicial
        blank=True
    )

    # Estado después del cambio (siempre requerido)
    estado_nuevo = models.ForeignKey(
        EstadoRadicado,
        on_delete=models.PROTECT,  # No borrar estados en uso
        related_name='historial_nuevo'
    )

    # Usuario que realizó el cambio
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT  # No borrar usuarios con historial
    )

    # Fecha automática del cambio
    fecha = models.DateTimeField(auto_now_add=True)

    # Comentarios opcionales sobre el cambio
    observacion = models.TextField(
        blank=True,
        null=True,
        help_text="Comentarios sobre el cambio de estado"
    )

    class Meta:
        # Ordenar por fecha descendente (más recientes primero)
        ordering = ['-fecha']

    def __str__(self):
        """
        Representación: 'Número → Estado (fecha)'
        Ejemplo: 'CER-DOC-20260415-0001 → Procesado (15/04/2026 14:30)'
        """
        return f"{self.radicado.numero} → {self.estado_nuevo} ({self.fecha:%d/%m/%Y %H:%M})"