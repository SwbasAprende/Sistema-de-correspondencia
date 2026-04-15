"""
Utilidades para generación de números y códigos.
"""

from django.utils import timezone


class GeneradorNumerosRadicado:
    """Genera números únicos para radicados."""

    @staticmethod
    def generar(empresa, tipo):
        """
        Genera un número único de radicado.

        Formato: EMPRESA-TIPO-FECHA-CONSECUTIVO
        Ejemplo: CER-DOC-20260415-0001

        Args:
            empresa: Instancia de Empresa o None (default CER)
            tipo: Instancia de TipoCorrespondencia

        Returns:
            str: Número único generado
        """
        # Importar aquí para evitar circular import
        from .models import Radicado

        ahora = timezone.now()

        # Construir prefijo
        empresa_codigo = empresa.codigo if empresa else 'CER'
        tipo_codigo = tipo.codigo if tipo else 'DOC'
        date_string = ahora.strftime('%Y%m%d')
        prefijo = f"{empresa_codigo}-{tipo_codigo}-{date_string}-"

        # Calcular siguiente consecutivo
        siguiente = GeneradorNumerosRadicado._calcular_siguiente_consecutivo(prefijo)

        return f"{prefijo}{siguiente:04d}"

    @staticmethod
    def _calcular_siguiente_consecutivo(prefijo):
        """Encuentra el próximo número consecutivo disponible."""
        # Importar aquí para evitar circular import
        from .models import Radicado

        ultimo = (
            Radicado.objects
            .filter(numero__startswith=prefijo)
            .order_by('-id')
            .values_list('numero', flat=True)
            .first()
        )

        if not ultimo:
            return 1

        try:
            # numero es: "CER-DOC-20260415-0001", extraer "0001"
            consecutivo = int(ultimo.split('-')[-1])
            return consecutivo + 1
        except (ValueError, IndexError):
            # Fallback: contar todos los del prefijo
            return Radicado.objects.filter(numero__startswith=prefijo).count() + 1