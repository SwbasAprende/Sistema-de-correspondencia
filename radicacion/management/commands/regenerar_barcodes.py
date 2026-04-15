import os

from django.core.management.base import BaseCommand

from radicacion.models import Radicado


class Command(BaseCommand):
    help = 'Regenera códigos de barras para radicados faltantes o con archivos dañados.'

    def handle(self, *args, **options):
        count = 0
        errors = 0

        for radicado in Radicado.objects.all():
            needs_regeneration = False
            try:
                if not radicado.codigo_barras:
                    needs_regeneration = True
                else:
                    barcode_path = radicado.codigo_barras.path
                    if not os.path.exists(barcode_path) or os.path.getsize(barcode_path) == 0:
                        needs_regeneration = True
            except (ValueError, OSError):
                needs_regeneration = True

            if needs_regeneration:
                try:
                    radicado._generar_codigo_barras()
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f'Regenerado: {radicado.numero}'))
                except Exception as exc:
                    errors += 1
                    self.stderr.write(self.style.ERROR(f'Error regenerando {radicado.numero}: {exc}'))

        self.stdout.write(self.style.SUCCESS(f'Total regenerados: {count}'))
        if errors:
            self.stderr.write(self.style.ERROR(f'Errores encontrados: {errors}'))
