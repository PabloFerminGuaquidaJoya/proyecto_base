"""
Centro de Control - Vistas de administración avanzada de usuarios.
Agregar estas funciones a usuarios/views.py e incluir las URLs correspondientes.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone

from .models import Usuario, TipoUsuario


@login_required
def centro_control_view(request):
    """
    Centro de control para administración de usuarios.
    Solo accesible por personal staff.
    """
    if not request.user.is_staff:
        return redirect('usuarios:dashboard')

    # ── Parámetros de búsqueda / filtrado ──────────────────────────────────
    q              = request.GET.get('q', '').strip()
    estado_filter  = request.GET.get('estado_filter', '').strip()
    programa_filter = request.GET.get('programa_filter', '').strip()

    # ── Queryset principal ─────────────────────────────────────────────────
    usuarios_qs = Usuario.objects.select_related('tipo_usuario').all()

    if q:
        usuarios_qs = usuarios_qs.filter(
            Q(nombres__icontains=q) |
            Q(apellidos__icontains=q) |
            Q(numero_documento__icontains=q) |
            Q(especialidad__icontains=q)
        )

    if estado_filter:
        usuarios_qs = usuarios_qs.filter(estado=estado_filter)

    if programa_filter:
        usuarios_qs = usuarios_qs.filter(
            Q(centro_formacion__icontains=programa_filter) |
            Q(especialidad__icontains=programa_filter)
        )

    usuarios_qs = usuarios_qs.order_by('-fecha_registro')

    # ── Pendientes (siempre la lista completa, sin filtros de búsqueda) ────
    pendientes = Usuario.objects.select_related('tipo_usuario').filter(
        estado='pendiente'
    ).order_by('fecha_registro')

    # ── Estadísticas globales ──────────────────────────────────────────────
    total           = Usuario.objects.count()
    activos         = Usuario.objects.filter(estado='activo').count()
    pendientes_count = Usuario.objects.filter(estado='pendiente').count()
    inactivos       = Usuario.objects.filter(
        Q(estado='inactivo') | Q(estado='suspendido')
    ).count()

    # ── Paginación ─────────────────────────────────────────────────────────
    paginator = Paginator(usuarios_qs, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # ── Tipos de usuario para el modal de edición ──────────────────────────
    tipos_usuario = TipoUsuario.objects.filter(activo=True).order_by('nombre')

    context = {
        'title': 'Centro de Control - SENA',
        'usuarios': page_obj.object_list,
        'pendientes': pendientes,
        'total': total,
        'activos': activos,
        'pendientes_count': pendientes_count,
        'inactivos': inactivos,
        'page_obj': page_obj,
        'tipos_usuario': tipos_usuario,
        'estado_choices': Usuario.ESTADO_CHOICES,
        # Valores actuales del formulario de búsqueda para repoblar inputs
        'form_search': {
            'q': q,
            'estado_filter': estado_filter,
            'programa_filter': programa_filter,
        },
    }

    return render(request, 'usuarios/centro_control.html', context)


@login_required
@require_POST
def admin_editar_usuario_ajax(request, pk):
    """
    Edición inline de un usuario vía AJAX (solo staff).
    Acepta POST con los campos básicos del usuario y devuelve JSON.
    """
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Sin permisos'}, status=403)

    usuario = get_object_or_404(Usuario, pk=pk)

    # ── Campos actualizables ───────────────────────────────────────────────
    campos_texto = [
        'nombres', 'apellidos', 'email', 'telefono',
        'cargo', 'especialidad', 'centro_formacion',
    ]

    for campo in campos_texto:
        valor = request.POST.get(campo, '').strip()
        if valor:
            setattr(usuario, campo, valor)

    # Estado
    nuevo_estado = request.POST.get('estado', '').strip()
    estados_validos = dict(Usuario.ESTADO_CHOICES)
    if nuevo_estado and nuevo_estado in estados_validos:
        usuario.estado = nuevo_estado
        if nuevo_estado == 'activo' and not usuario.fecha_aprobacion:
            usuario.fecha_aprobacion = timezone.now()

    # Tipo de usuario (FK)
    tipo_usuario_id = request.POST.get('tipo_usuario_id', '').strip()
    if tipo_usuario_id:
        try:
            tipo_usuario = TipoUsuario.objects.get(pk=int(tipo_usuario_id), activo=True)
            usuario.tipo_usuario = tipo_usuario
        except (TipoUsuario.DoesNotExist, ValueError):
            return JsonResponse(
                {'success': False, 'message': 'Tipo de usuario no válido'},
                status=400
            )

    # Validación básica de email único
    email = request.POST.get('email', '').strip()
    if email:
        if Usuario.objects.exclude(pk=pk).filter(email=email).exists():
            return JsonResponse(
                {'success': False, 'message': 'Ya existe un usuario con ese email'},
                status=400
            )
        usuario.email = email

    try:
        usuario.save()
        return JsonResponse({
            'success': True,
            'message': f'Usuario {usuario.nombre_completo} actualizado correctamente',
        })
    except Exception as exc:
        return JsonResponse(
            {'success': False, 'message': f'Error al guardar: {str(exc)}'},
            status=500
        )
