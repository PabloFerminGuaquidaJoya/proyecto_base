# -*- coding: utf-8 -*-
"""
Context processors globales para el sistema.
"""
from django.db import OperationalError


def backup_permisos(request):
    """
    Agrega `puede_crear_backup` al contexto de todos los templates.
    True para los roles: Administrador, Staff-sistema, Instructor y variantes.
    """
    if not request.user.is_authenticated:
        return {'puede_crear_backup': False}

    try:
        from usuarios.models import Usuario
        usuario = Usuario.objects.select_related('tipo_usuario').get(
            numero_documento=request.user.username
        )
        cargo = (usuario.cargo or '').lower()
        tipo = (usuario.tipo_usuario.nombre or '').lower() if usuario.tipo_usuario else ''
        palabras_clave = ('instructor', 'administrador', 'admin', 'staff')
        puede = any(p in cargo for p in palabras_clave) or any(p in tipo for p in palabras_clave)
    except Exception:
        # Fallback: si no se puede leer el perfil, usar el flag is_staff de Django
        puede = request.user.is_staff

    return {'puede_crear_backup': puede}
