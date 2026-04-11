from .models import Usuario


# Roles que tienen acceso completo a todos los módulos
_ROLES_ADMIN  = ('administrador', 'admin', 'staff')
_ROLES_INST   = ('instructor',)
_ROLES_MANT   = ('personal de mantenimiento',)
_ROLES_APREN  = ('aprendiz', 'invitado')


def _contiene(texto, opciones):
    t = (texto or '').lower()
    return any(o in t for o in opciones)


def usuario_actual(request):
    if not request.user.is_authenticated:
        return {
            'usuario_actual': None,
            'estado_usuario': None,
            'es_pendiente': False,
            'nav_maquinaria': False,
            'nav_inventario': False,
            'nav_reportes': False,
            'nav_documentos': False,
            'nav_backups': False,
            'nav_gestion_usuarios': False,
            'nav_centro_admin': False,
        }

    try:
        usuario = Usuario.objects.select_related('tipo_usuario').get(
            numero_documento=request.user.username
        )
        estado = usuario.estado
        tipo   = usuario.tipo_usuario.nombre if usuario.tipo_usuario else ''
        cargo  = usuario.cargo or ''

        es_admin  = _contiene(tipo, _ROLES_ADMIN)  or _contiene(cargo, _ROLES_ADMIN)
        es_inst   = _contiene(tipo, _ROLES_INST)   or _contiene(cargo, _ROLES_INST)
        es_mant   = _contiene(tipo, _ROLES_MANT)   or _contiene(cargo, _ROLES_MANT)

        activo = estado == 'activo'

        # Pendiente → permisos de Aprendiz (mínimos)
        if estado == 'pendiente' or not activo:
            nav_maquinaria      = False
            nav_inventario      = False
            nav_reportes        = False
            nav_documentos      = True
            nav_backups         = False
            nav_gestion_usuarios = False
            nav_centro_admin    = False
        elif es_admin:
            nav_maquinaria      = True
            nav_inventario      = True
            nav_reportes        = True
            nav_documentos      = True
            nav_backups         = True
            nav_gestion_usuarios = True
            nav_centro_admin    = True
        elif es_inst:
            nav_maquinaria      = True
            nav_inventario      = True
            nav_reportes        = True
            nav_documentos      = True
            nav_backups         = True
            nav_gestion_usuarios = False
            nav_centro_admin    = False
        elif es_mant:
            nav_maquinaria      = True
            nav_inventario      = False
            nav_reportes        = False
            nav_documentos      = True
            nav_backups         = False
            nav_gestion_usuarios = False
            nav_centro_admin    = False
        else:
            # Aprendiz / Invitado activo
            nav_maquinaria      = True
            nav_inventario      = False
            nav_reportes        = False
            nav_documentos      = True
            nav_backups         = False
            nav_gestion_usuarios = False
            nav_centro_admin    = False

        return {
            'usuario_actual':       usuario,
            'estado_usuario':       estado,
            'es_pendiente':         estado == 'pendiente',
            'nav_maquinaria':       nav_maquinaria,
            'nav_inventario':       nav_inventario,
            'nav_reportes':         nav_reportes,
            'nav_documentos':       nav_documentos,
            'nav_backups':          nav_backups,
            'nav_gestion_usuarios': nav_gestion_usuarios,
            'nav_centro_admin':     nav_centro_admin,
        }

    except Usuario.DoesNotExist:
        return {
            'usuario_actual': None,
            'estado_usuario': None,
            'es_pendiente': False,
            'nav_maquinaria': False,
            'nav_inventario': False,
            'nav_reportes': False,
            'nav_documentos': True,
            'nav_backups': False,
            'nav_gestion_usuarios': False,
            'nav_centro_admin': False,
        }
