from .models import Usuario


def usuario_actual(request):
    if request.user.is_authenticated:
        try:
            usuario = Usuario.objects.get(numero_documento=request.user.username)
            return {'usuario_actual': usuario}
        except Usuario.DoesNotExist:
            pass
    return {'usuario_actual': None}
