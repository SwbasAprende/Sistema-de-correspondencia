from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db import models
from .models import Radicado, EstadoRadicado, TipoCorrespondencia
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

def get_rol(user):
    try:
        return user.perfil.rol
    except:
        return 'consultor'
    
@login_required
def lista_radicados(request):
    radicados = Radicado.objects.all().order_by('-fecha')
    q = request.GET.get('q')
    if q:
        radicados = radicados.filter(
            models.Q(numero__icontains=q) |
            models.Q(remitente__icontains=q) |
            models.Q(asunto__icontains=q)
        )
    direccion = request.GET.get('direccion')
    if direccion:
        radicados = radicados.filter(direccion=direccion)
    rol = get_rol(request.user)
    return render(request, 'radicacion/lista.html', {'radicados': radicados, 'rol': rol})

@login_required
def crear_radicado(request):
    rol = get_rol(request.user)
    if rol == 'consultor':
        return redirect('lista')

    if request.method == 'POST':
        from datetime import date
        año = date.today().year
        ultimo = Radicado.objects.order_by('-id').first()
        siguiente = (ultimo.id + 1) if ultimo else 1
        numero = f"RAD-{siguiente:04d}-{año}"

        remitente = request.POST.get('remitente')
        destinatario = request.POST.get('destinatario')
        asunto = request.POST.get('asunto')
        direccion = request.POST.get('direccion')
        tipo_id = request.POST.get('tipo')
        estado_id = request.POST.get('estado')
        documento = request.FILES.get('documento')

        radicado = Radicado(
            numero=numero,
            remitente=remitente,
            destinatario=destinatario,
            asunto=asunto,
            direccion=direccion,
            tipo_id=tipo_id,
            estado_id=estado_id,
            documento=documento,
            usuario=request.user
        )
        radicado.save()
        return redirect('detalle', pk=radicado.pk)

    tipos = TipoCorrespondencia.objects.all()
    estados = EstadoRadicado.objects.all()
    return render(request, 'radicacion/crear.html', {'tipos': tipos, 'estados': estados})

@login_required
def detalle_radicado(request, pk):
    radicado = get_object_or_404(Radicado, pk=pk)
    estados = EstadoRadicado.objects.all()
    return render(request, 'radicacion/detalle.html', {'radicado': radicado, 'estados': estados})

@login_required
def cambiar_estado(request, pk):
    radicado = get_object_or_404(Radicado, pk=pk)
    if request.method == 'POST':
        estado_id = request.POST.get('estado')
        radicado.estado_id = estado_id
        radicado.save()
        return redirect('detalle', pk=pk)
    return redirect('detalle', pk=pk)

@login_required
def dashboard(request):
    total = Radicado.objects.count()
    recibidos = Radicado.objects.filter(direccion='recibido').count()
    enviados = Radicado.objects.filter(direccion='enviado').count()
    ultimos = Radicado.objects.all().order_by('-id')[:5]
    estados = EstadoRadicado.objects.all()
    por_estado = []
    for estado in estados:
        count = Radicado.objects.filter(estado=estado).count()
        porcentaje = round((count / total * 100), 1) if total > 0 else 0
        por_estado.append({'nombre': estado.nombre, 'count': count, 'porcentaje': porcentaje})
    return render(request, 'radicacion/dashboard.html', {
        'total': total, 'recibidos': recibidos, 'enviados': enviados,
        'por_estado': por_estado, 'ultimos': ultimos
    })


@login_required
def imprimir_sticker(request, pk):
    radicado = get_object_or_404(Radicado, pk=pk)
    return render(request, 'radicacion/sticker.html', {'radicado': radicado})

    from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

@login_required
def exportar_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="radicados.pdf"'

    doc = SimpleDocTemplate(response, pagesize=landscape(letter))
    elementos = []
    styles = getSampleStyleSheet()

    titulo = Paragraph("<b>Lista de Radicados - Centro de Estudios Regionales</b>", styles['Title'])
    elementos.append(titulo)
    elementos.append(Spacer(1, 20))

    radicados = Radicado.objects.all().order_by('-fecha')
    datos = [['Número', 'Fecha', 'Dirección', 'Remitente', 'Asunto', 'Tipo', 'Estado']]

    for r in radicados:
        datos.append([
            str(r.numero),
            str(r.fecha),
            r.get_direccion_display(),
            r.remitente,
            r.asunto[:50],
            str(r.tipo),
            str(r.estado),
        ])

    tabla = Table(datos, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a3a5c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f0f8')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#a8c4e0')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))

    elementos.append(tabla)
    doc.build(elementos)
    return response


@login_required
def exportar_excel(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="radicados.xlsx"'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Radicados'

    encabezados = ['Número', 'Fecha', 'Dirección', 'Remitente', 'Destinatario', 'Asunto', 'Tipo', 'Estado', 'Usuario']
    for col, titulo in enumerate(encabezados, 1):
        cell = ws.cell(row=1, column=col, value=titulo)
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill(start_color='1a3a5c', end_color='1a3a5c', fill_type='solid')
        cell.alignment = Alignment(horizontal='center')

    radicados = Radicado.objects.all().order_by('-fecha')
    for row, r in enumerate(radicados, 2):
        ws.cell(row=row, column=1, value=r.numero)
        ws.cell(row=row, column=2, value=str(r.fecha))
        ws.cell(row=row, column=3, value=r.get_direccion_display())
        ws.cell(row=row, column=4, value=r.remitente)
        ws.cell(row=row, column=5, value=r.destinatario or '')
        ws.cell(row=row, column=6, value=r.asunto)
        ws.cell(row=row, column=7, value=str(r.tipo))
        ws.cell(row=row, column=8, value=str(r.estado))
        ws.cell(row=row, column=9, value=str(r.usuario))

    for col in ws.columns:
        max_length = max(len(str(cell.value or '')) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = min(max_length + 4, 40)

    wb.save(response)
    return response

@login_required
def ayuda(request):
    rol = get_rol(request.user)
    return render(request, 'radicacion/ayuda.html', {'rol': rol})