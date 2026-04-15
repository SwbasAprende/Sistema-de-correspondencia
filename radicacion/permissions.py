"""
Gestión de permisos y roles.
"""

from typing import Literal
from django.contrib.auth.models import User


ROLES = Literal['administrador', 'operador', 'consultor']


class GestorRoles:
    """Centraliza toda lógica de roles y permisos del usuario."""

    @staticmethod
    def obtener_rol(usuario: User) -> ROLES:
        """
        Obtiene el rol del usuario.

        Args:
            usuario: Usuario Django

        Returns:
            'administrador', 'operador' o 'consultor' (default)
        """
        try:
            return usuario.perfil.rol
        except AttributeError:
            return 'consultor'

    @staticmethod
    def puede_crear_radicado(usuario: User) -> bool:
        """Verifica si el usuario puede crear radicados."""
        rol = GestorRoles.obtener_rol(usuario)
        return rol in ['administrador', 'operador']

    @staticmethod
    def puede_cambiar_estado(usuario: User) -> bool:
        """Verifica si el usuario puede cambiar estados."""
        rol = GestorRoles.obtener_rol(usuario)
        return rol in ['administrador', 'operador']

    @staticmethod
    def puede_exportar(usuario: User) -> bool:
        """Verifica si el usuario puede exportar datos."""
        rol = GestorRoles.obtener_rol(usuario)
        return rol in ['administrador', 'operador', 'consultor']  # Todos