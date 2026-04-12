from .models import Usuario


def usuario_actual(request):
    if request.user.is_authenticated:
        try:
            usuario = Usuario.objects.get(numero_documento=request.user.username)
            # Si el usuario está pendiente de aprobación, su cargo efectivo es Aprendiz
            # independientemente del rol que tenga asignado
            cargo_efectivo = usuario.cargo
            if usuario.estado == 'pendiente':
                cargo_efectivo = 'Aprendiz'
            return {
                'usuario_actual': usuario,
                'cargo_efectivo': cargo_efectivo,
            }
        except Usuario.DoesNotExist:
            pass
    return {'usuario_actual': None, 'cargo_efectivo': None}
