from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from . import detector


@login_required
@require_POST
def detectar_view(request):
    """
    POST /vision/api/detectar/
    Acepta multipart con campo 'imagen'.
    Retorna JSON con resultado de detección.
    """
    if 'imagen' not in request.FILES:
        return JsonResponse({'error': "Falta el campo 'imagen'."}, status=400)

    imagen_bytes = request.FILES['imagen'].read()
    resultado = detector.detectar(imagen_bytes)
    return JsonResponse(resultado)


@login_required
def estado_view(request):
    """GET /vision/api/estado/ — estado del sistema de IA."""
    return JsonResponse(detector.estado())
