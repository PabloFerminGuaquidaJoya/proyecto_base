# -*- coding: utf-8 -*-
"""
Context processors globales para el sistema.
"""
from django.db import OperationalError


def backup_permisos(request):
    """
    Agrega `puede_crear_backup` al contexto de todos los templates.
    True si el usuario tiene cargo de instructor o administrador.
    """
    if not request.user.is_authenticated:
        return {'puede_crear_backup': False}

    try:
        from usuarios.models import Usuario
        usuario = Usuario.objects.select_related('tipo_usuario').get(
            numero_documento=request.user.username
        )
        cargo = (usuario.cargo or '').lower()
        tipo = ''
        if usuario.tipo_usuario:
            tipo = (usuario.tipo_usuario.nombre or '').lower()
        palabras_clave = ('instructor', 'administrador', 'admin', 'staff')
        puede = any(p in cargo for p in palabras_clave) or any(p in tipo for p in palabras_clave)
    except Exception:
        puede = False

    return {'puede_crear_backup': puede}
