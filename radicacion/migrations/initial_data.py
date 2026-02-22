from django.db import migrations

def cargar_datos_iniciales(apps, schema_editor):
    TipoCorrespondencia = apps.get_model('radicacion', 'TipoCorrespondencia')
    EstadoRadicado = apps.get_model('radicacion', 'EstadoRadicado')

    tipos = [
        'Oficio',
        'Circular',
        'Memorando',
        'Contrato',
        'Derecho de Petición',
        'Resolución',
        'Factura',
        'Informe',
    ]

    estados = [
        'Recibido',
        'En revisión',
        'En trámite',
        'Respondido',
        'Archivado',
    ]

    for tipo in tipos:
        TipoCorrespondencia.objects.get_or_create(nombre=tipo)

    for estado in estados:
        EstadoRadicado.objects.get_or_create(nombre=estado)

class Migration(migrations.Migration):

    dependencies = [
        ('radicacion', '0005_rename_usuario_perfil_user_alter_radicado_numero'),
    ]

    operations = [
        migrations.RunPython(cargar_datos_iniciales),
    ]