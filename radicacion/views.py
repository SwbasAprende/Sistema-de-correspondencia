import os
from io import BytesIO
from datetime import datetime

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from .models import Radicado, EstadoRadicado, TipoCorrespondencia, Empresa, HistorialEstado
from .permissions import GestorRoles
from .services import ExportadorRadicados

def get_rol(user):
    try:
        return user.perfil.rol
    except AttributeError:
        return 'consultor'
    
@login_required
def lista_radicados(request):
    """
    Muestra la lista de radicados con filtros de búsqueda.

    GET params:
    - q: búsqueda por número, remitente o asunto
    - direccion: filtro por 'recibido' o 'enviado'

    Renderiza: radicacion/lista.html
    """
    # Obtener todos los radicados ordenados por fecha (más recientes primero)
    radicados = Radicado.objects.all().order_by('-fecha')

    # Filtro de búsqueda por texto (q)
    q = request.GET.get('q')
    if q:
        # Buscar en número, remitente o asunto (case insensitive)
        radicados = radicados.filter(
            models.Q(numero__icontains=q) |
            models.Q(remitente__icontains=q) |
            models.Q(asunto__icontains=q)
        )

    # Filtro por dirección (recibido/enviado)
    direccion = request.GET.get('direccion')
    if direccion:
        radicados = radicados.filter(direccion=direccion)

    # Obtener rol del usuario para mostrar/ocultar acciones
    rol = GestorRoles.obtener_rol(request.user)

    return render(request, 'radicacion/lista.html', {
        'radicados': radicados,
        'rol': rol
    })

@login_required
def crear_radicado(request):
    """
    Maneja la creación de un nuevo radicado.

    GET: Muestra formulario de creación
    POST: Procesa datos y crea radicado

    Permisos: Operador o Administrador (consultores redirigidos)
    Renderiza: radicacion/crear.html
    Redirige: detalle del radicado creado
    """
    # Verificar permisos: solo operadores y administradores pueden crear
    if not GestorRoles.puede_crear_radicado(request.user):
        return redirect('lista')

    if request.method == 'POST':
        # Extraer datos del formulario
        remitente = request.POST.get('remitente')
        destinatario = request.POST.get('destinatario')
        asunto = request.POST.get('asunto')
        direccion = request.POST.get('direccion')
        tipo_id = request.POST.get('tipo')
        estado_id = request.POST.get('estado')
        empresa_id = request.POST.get('empresa')
        documento = request.FILES.get('documento')  # Archivo opcional

        # Crear objeto Radicado (aún no guardado)
        radicado = Radicado(
            remitente=remitente,
            destinatario=destinatario,
            asunto=asunto,
            direccion=direccion,
            tipo_id=tipo_id,
            estado_id=estado_id,
            empresa_id=empresa_id if empresa_id else None,  # None = CER por defecto
            documento=documento,
            usuario=request.user,  # Usuario que crea
        )

        # Guardar: genera número automático y código de barras
        radicado.save()

        # Registrar en historial: primer cambio (creación)
        HistorialEstado.objects.create(
            radicado=radicado,
            estado_anterior=None,  # No hay estado anterior
            estado_nuevo=radicado.estado,  # Estado inicial
            usuario=request.user,
            observacion='Radicado creado'
        )

        # Redirigir a la página de detalle
        return redirect('detalle', pk=radicado.pk)

    # GET: mostrar formulario con datos para selects
    tipos = TipoCorrespondencia.objects.all()
    estados = EstadoRadicado.objects.all()
    empresas = Empresa.objects.all()

    return render(request, 'radicacion/crear.html', {
        'tipos': tipos,
        'estados': estados,
        'empresas': empresas
    })

@login_required
def detalle_radicado(request, pk):
    """
    Muestra el detalle completo de un radicado y su historial.

    Args:
        pk: ID del radicado

    Renderiza: radicacion/detalle.html con:
    - radicado: objeto completo
    - estados: lista para cambiar estado
    - historial: cambios ordenados por fecha
    """
    # Obtener radicado o 404 si no existe
    radicado = get_object_or_404(Radicado, pk=pk)

    # Obtener todos los estados para el select de cambio
    estados = EstadoRadicado.objects.all()

    # Obtener historial con related objects para evitar queries N+1
    historial = radicado.historial.select_related(
        'estado_anterior',
        'estado_nuevo',
        'usuario'
    ).all()

    return render(request, 'radicacion/detalle.html', {
        'radicado': radicado,
        'estados': estados,
        'historial': historial
    })

@login_required
def cambiar_estado(request, pk):
    """
    Cambia el estado de un radicado y registra el cambio en el historial.

    POST params:
    - estado: ID del nuevo estado
    - observacion: comentario opcional

    Permisos: Operador o Administrador
    Redirige: de vuelta al detalle
    """
    # Obtener radicado o 404
    radicado = get_object_or_404(Radicado, pk=pk)

    if request.method == 'POST':
        # Guardar estado anterior para comparación
        estado_anterior = radicado.estado

        # Obtener nuevo estado del form
        estado_id = request.POST.get('estado')
        observacion = request.POST.get('observacion', '').strip()

        # Actualizar estado del radicado
        radicado.estado_id = estado_id
        radicado.save()

        # Solo registrar en historial si el estado realmente cambió
        if str(estado_anterior.pk) != str(estado_id):
            HistorialEstado.objects.create(
                radicado=radicado,
                estado_anterior=estado_anterior,
                estado_nuevo=radicado.estado,
                usuario=request.user,
                observacion=observacion or None  # None si vacío
            )

    # Redirigir de vuelta al detalle (siempre, GET o POST)
    return redirect('detalle', pk=pk)

@login_required
def dashboard(request):
    """
    Muestra el dashboard principal con estadísticas del sistema.

    Calcula:
    - Total de radicados
    - Conteo por dirección (recibidos/enviados)
    - Últimos 5 radicados
    - Distribución por estado con porcentajes

    Renderiza: radicacion/dashboard.html
    """
    # Estadísticas básicas
    total = Radicado.objects.count()
    recibidos = Radicado.objects.filter(direccion='recibido').count()
    enviados = Radicado.objects.filter(direccion='enviado').count()

    # Últimos 5 radicados (ordenados por ID descendente = más recientes)
    ultimos = Radicado.objects.all().order_by('-id')[:5]

    # Distribución por estado con porcentajes
    estados = EstadoRadicado.objects.all()
    por_estado = []
    for estado in estados:
        count = Radicado.objects.filter(estado=estado).count()
        # Calcular porcentaje (evitar división por cero)
        porcentaje = round((count / total * 100), 1) if total > 0 else 0
        por_estado.append({
            'nombre': estado.nombre,
            'count': count,
            'porcentaje': porcentaje
        })

    return render(request, 'radicacion/dashboard.html', {
        'total': total,
        'recibidos': recibidos,
        'enviados': enviados,
        'por_estado': por_estado,
        'ultimos': ultimos
    })

@login_required
def imprimir_sticker(request, pk):
    """
    Muestra la página de impresión de sticker/código de barras.

    Args:
        pk: ID del radicado

    Renderiza: radicacion/sticker.html (página optimizada para impresión)
    """
    radicado = get_object_or_404(Radicado, pk=pk)
    return render(request, 'radicacion/sticker.html', {'radicado': radicado})

@login_required
def barcode_image(request, pk):
    """
    Sirve la imagen del código de barras del radicado.

    Esta ruta evita depender de la configuración de archivos media del servidor.
    """
    radicado = get_object_or_404(Radicado, pk=pk)

    if not radicado.codigo_barras or not os.path.exists(radicado.codigo_barras.path):
        radicado._generar_codigo_barras()

    try:
        return FileResponse(radicado.codigo_barras.open('rb'), content_type='image/png')
    except (ValueError, FileNotFoundError):
        raise Http404("Código de barras no disponible.")

@login_required
def exportar_pdf(request):
    """Descarga lista de radicados en PDF."""
    return ExportadorRadicados.exportar_a_pdf()

@login_required
def exportar_excel(request):
    """Descarga lista de radicados en Excel."""
    return ExportadorRadicados.exportar_a_excel()

@login_required
def ayuda(request):
    """
    Muestra la página de ayuda del sistema.

    El contenido puede variar según el rol del usuario.

    Renderiza: radicacion/ayuda.html
    """
    rol = GestorRoles.obtener_rol(request.user)
    return render(request, 'radicacion/ayuda.html', {'rol': rol})