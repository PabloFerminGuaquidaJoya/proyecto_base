from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.cache import cache
import secrets
import json
import logging
from datetime import timedelta

from .models import Usuario, TipoUsuario, SesionUsuario, TokenRecuperacionPassword, ReconocimientoFacial, IntentoReconocimientoFacial
from .forms import (
    LoginForm, UsuarioForm, RegistroUsuarioForm, PerfilUsuarioForm,
    CambiarPasswordForm, BuscarUsuariosForm, RecuperarPasswordForm, ResetPasswordForm
)
from .facial_recognition import facial_service

# Configuración de logging
logger = logging.getLogger(__name__)

# Rate limiting - Constantes
RATE_LIMIT_FACIAL_LOGIN = 5  # máximo 5 intentos
RATE_LIMIT_WINDOW = 300  # en 5 minutos (300 segundos)

def login_view(request):
    """Vista de inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')

    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Intentar autenticar por número de documento o email
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                # Registrar sesión
                try:
                    usuario = Usuario.objects.get(numero_documento=username)
                    SesionUsuario.objects.create(
                        usuario=usuario,
                        token_sesion=request.session.session_key or '',
                        ip_address=request.META.get('REMOTE_ADDR', ''),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                    # Actualizar último acceso
                    usuario.ultimo_acceso = timezone.now()
                    usuario.save()
                except Usuario.DoesNotExist:
                    pass

                messages.success(request, f'¡Bienvenido!')
                return redirect('usuarios:dashboard')
            else:
                messages.error(request, 'Credenciales inválidas')

    return render(request, 'usuarios/modern_login.html', {
        'form': form,
        'title': 'Iniciar Sesión - SENA'
    })

@login_required
def logout_view(request):
    """Vista de cierre de sesión"""
    try:
        usuario = Usuario.objects.get(numero_documento=request.user.username)
        usuario.sesiones.filter(activa=True).update(
            fecha_fin=timezone.now(),
            activa=False
        )
    except Usuario.DoesNotExist:
        pass

    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente')
    return redirect('usuarios:login')

@login_required
def dashboard_view(request):
    """Dashboard principal después del login"""
    # Estadísticas básicas de maquinaria
    total_maquinas = 0
    maquinas_operativas = 0
    maquinas_mantenimiento = 0
    alertas_activas = 0
    maquinas_disponibles = 0
    maquinas_fuera_servicio = 0

    try:
        from maquinaria.models import Maquina, AlertaMaquina

        # Estadísticas principales
        total_maquinas = Maquina.objects.count()
        maquinas_operativas = Maquina.objects.filter(estado='operativa').count()
        maquinas_mantenimiento = Maquina.objects.filter(estado='mantenimiento').count()
        maquinas_disponibles = Maquina.objects.filter(estado='disponible').count()
        maquinas_fuera_servicio = Maquina.objects.filter(estado='fuera_servicio').count()
        alertas_activas = AlertaMaquina.objects.filter(estado='activa').count()

    except ImportError:
        pass

    # Actividad reciente del sistema
    actividades_recientes = []
    try:
        from maquinaria.models import HistorialMaquina
        actividades_recientes = HistorialMaquina.objects.select_related('maquina', 'usuario').order_by('-fecha_evento')[:5]
    except ImportError:
        pass

    # Estadísticas adicionales
    try:
        usuario_actual = Usuario.objects.get(numero_documento=request.user.username)
        maquinas_asignadas = Maquina.objects.filter(responsable=usuario_actual).count()
    except Usuario.DoesNotExist:
        usuario_actual = None
        maquinas_asignadas = 0

    context = {
        'title': 'Dashboard - SENA',
        'total_maquinas': total_maquinas,
        'maquinas_operativas': maquinas_operativas,
        'maquinas_mantenimiento': maquinas_mantenimiento,
        'maquinas_disponibles': maquinas_disponibles,
        'maquinas_fuera_servicio': maquinas_fuera_servicio,
        'alertas_activas': alertas_activas,
        'actividades_recientes': actividades_recientes,
        'maquinas_asignadas': maquinas_asignadas,
        'usuario_actual': usuario_actual,
    }

    return render(request, 'usuarios/dashboard.html', context)

@login_required
def perfil_view(request):
    """Vista del perfil de usuario"""
    try:
        usuario = Usuario.objects.get(numero_documento=request.user.username)
    except Usuario.DoesNotExist:
        messages.error(request, 'Perfil de usuario no encontrado')
        return redirect('usuarios:dashboard')

    form = PerfilUsuarioForm(instance=usuario)
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            usuario_actualizado = form.save(commit=False)
            # Sincronizar tipo_usuario con el cargo seleccionado
            nuevo_cargo = form.cleaned_data.get('cargo', '')
            if usuario.cargo == 'Aprendiz':
                # Restaurar campos protegidos para aprendices
                usuario_actualizado.centro_formacion = usuario.centro_formacion
                usuario_actualizado.especialidad = usuario.especialidad
                usuario_actualizado.cargo = usuario.cargo
            elif nuevo_cargo:
                tipo_usuario, _ = TipoUsuario.objects.get_or_create(
                    nombre=nuevo_cargo,
                    defaults={'descripcion': f'{nuevo_cargo} SENA', 'permisos': {}, 'activo': True}
                )
                usuario_actualizado.tipo_usuario = tipo_usuario
            usuario_actualizado.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('usuarios:perfil')

    tiene_reconocimiento_facial = ReconocimientoFacial.objects.filter(usuario=usuario, activo=True).exists()

    return render(request, 'usuarios/perfil.html', {
        'form': form,
        'usuario': usuario,
        'tiene_reconocimiento_facial': tiene_reconocimiento_facial,
        'title': 'Mi Perfil - SENA'
    })

@login_required
def lista_usuarios_view(request):
    """Vista para listar usuarios (solo admin)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página')
        return redirect('usuarios:dashboard')

    form = BuscarUsuariosForm(request.GET or None)
    usuarios = Usuario.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get('query')
        tipo_usuario = form.cleaned_data.get('tipo_usuario')
        estado = form.cleaned_data.get('estado')
        centro_formacion = form.cleaned_data.get('centro_formacion')

        if query:
            usuarios = usuarios.filter(
                Q(nombres__icontains=query) |
                Q(apellidos__icontains=query) |
                Q(numero_documento__icontains=query) |
                Q(email__icontains=query)
            )
        if tipo_usuario:
            usuarios = usuarios.filter(tipo_usuario=tipo_usuario)
        if estado:
            usuarios = usuarios.filter(estado=estado)
        if centro_formacion:
            usuarios = usuarios.filter(centro_formacion=centro_formacion)

    paginator = Paginator(usuarios.order_by('-fecha_registro'), 20)
    page = request.GET.get('page')
    usuarios = paginator.get_page(page)

    return render(request, 'usuarios/lista_usuarios.html', {
        'form': form,
        'usuarios': usuarios,
        'title': 'Gestión de Usuarios - SENA'
    })

@login_required
def crear_usuario_view(request):
    """Vista para crear usuario (solo admin)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página')
        return redirect('usuarios:dashboard')

    form = UsuarioForm()
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save(commit=False)
            try:
                usuario.created_by = Usuario.objects.get(numero_documento=request.user.username)
            except Usuario.DoesNotExist:
                pass
            usuario.save()
            messages.success(request, f'Usuario {usuario.nombre_completo} creado correctamente')
            return redirect('usuarios:lista')

    return render(request, 'usuarios/crear_usuario.html', {
        'form': form,
        'title': 'Crear Usuario - SENA'
    })

@login_required
def editar_usuario_view(request, pk):
    """Vista para editar usuario (solo admin)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página')
        return redirect('usuarios:dashboard')

    usuario = get_object_or_404(Usuario, pk=pk)
    form = UsuarioForm(instance=usuario)

    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario {usuario.nombre_completo} actualizado correctamente')
            return redirect('usuarios:lista')

    return render(request, 'usuarios/editar_usuario.html', {
        'form': form,
        'usuario': usuario,
        'title': f'Editar {usuario.nombre_completo} - SENA'
    })

@login_required
def detalle_usuario_view(request, pk):
    """Vista de detalle de usuario"""
    usuario = get_object_or_404(Usuario, pk=pk)

    # Solo admin o el mismo usuario puede ver detalles
    if not request.user.is_staff and request.user.username != usuario.numero_documento:
        messages.error(request, 'No tienes permisos para ver esta información')
        return redirect('usuarios:dashboard')

    # Estadísticas adicionales
    sesiones_recientes = SesionUsuario.objects.filter(
        usuario=usuario
    ).order_by('-fecha_inicio')[:10]

    return render(request, 'usuarios/detalle_usuario.html', {
        'usuario': usuario,
        'sesiones_recientes': sesiones_recientes,
        'title': f'{usuario.nombre_completo} - SENA'
    })

@login_required
@require_http_methods(["POST"])
def cambiar_estado_usuario(request, pk):
    """Vista para cambiar estado de usuario (solo admin)"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Sin permisos'}, status=403)

    usuario = get_object_or_404(Usuario, pk=pk)
    nuevo_estado = request.POST.get('estado')

    if nuevo_estado in dict(Usuario.ESTADO_CHOICES):
        usuario.estado = nuevo_estado
        if nuevo_estado == 'activo':
            usuario.fecha_aprobacion = timezone.now()
        usuario.save()

        return JsonResponse({'success': True, 'estado': usuario.get_estado_display()})

    return JsonResponse({'error': 'Estado no válido'}, status=400)

@login_required
@require_http_methods(["POST"])
def admin_eliminar_usuario_ajax(request, pk):
    """Eliminación de usuario vía AJAX — solo staff."""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Sin permisos'}, status=403)

    usuario = get_object_or_404(Usuario, pk=pk)

    if usuario.numero_documento == request.user.username:
        return JsonResponse(
            {'success': False, 'message': 'No puedes eliminar tu propia cuenta.'},
            status=400
        )

    nombre = usuario.nombre_completo

    try:
        User.objects.filter(username=usuario.numero_documento).delete()
    except Exception:
        pass

    usuario.delete()

    return JsonResponse({'success': True, 'message': f'Usuario {nombre} eliminado correctamente.'})


@login_required
def centro_control_view(request):
    """Centro de control de administración de usuarios — solo staff."""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('usuarios:dashboard')

    q               = request.GET.get('q', '').strip()
    estado_filter   = request.GET.get('estado_filter', '').strip()
    programa_filter = request.GET.get('programa_filter', '').strip()

    usuarios_qs = Usuario.objects.select_related('tipo_usuario', 'centro_formacion', 'ficha').all()

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
            Q(centro_formacion__nombre__icontains=programa_filter) |
            Q(especialidad__icontains=programa_filter)
        )

    usuarios_qs = usuarios_qs.order_by('-fecha_registro')

    pendientes       = Usuario.objects.select_related('tipo_usuario').filter(estado='pendiente').order_by('fecha_registro')
    total            = Usuario.objects.count()
    activos          = Usuario.objects.filter(estado='activo').count()
    pendientes_count = Usuario.objects.filter(estado='pendiente').count()
    inactivos        = Usuario.objects.filter(Q(estado='inactivo') | Q(estado='suspendido')).count()
    tipos_usuario    = TipoUsuario.objects.filter(activo=True).order_by('nombre')
    from sistema.models import CentroFormacion as CF, Ficha as F
    centros_lista = CF.objects.filter(activo=True).order_by('nombre')
    fichas_lista  = F.objects.filter(activo=True).order_by('numero')

    paginator   = Paginator(usuarios_qs, 15)
    page_obj    = paginator.get_page(request.GET.get('page'))

    # ── Personal de Mantenimiento ────────────────────────────────────────
    q_mant      = request.GET.get('q_mant', '').strip()
    estado_mant = request.GET.get('estado_mant', '').strip()
    cargo_mant  = request.GET.get('cargo_mant', '').strip()

    from django.db.models import Count, Max, Q as DQ

    personal_mant_qs = (
        Usuario.objects
        .filter(cargo='Personal de Mantenimiento')
        .select_related('tipo_usuario', 'centro_formacion')
        .annotate(
            total_asignados=Count(
                'mantenimientos_asignados',
                distinct=True
            ),
            total_completados=Count(
                'mantenimientos_asignados',
                filter=DQ(mantenimientos_asignados__estado='completado'),
                distinct=True
            ),
            total_en_progreso=Count(
                'mantenimientos_asignados',
                filter=DQ(mantenimientos_asignados__estado='en_progreso'),
                distinct=True
            ),
            total_programados=Count(
                'mantenimientos_asignados',
                filter=DQ(mantenimientos_asignados__estado='programado'),
                distinct=True
            ),
            ultimo_mantenimiento=Max('mantenimientos_asignados__fecha_fin_real'),
            total_maquinas=Count(
                'mantenimientos_asignados__maquina',
                distinct=True
            ),
        )
        .order_by('nombres', 'apellidos')
    )

    if q_mant:
        personal_mant_qs = personal_mant_qs.filter(
            DQ(nombres__icontains=q_mant) |
            DQ(apellidos__icontains=q_mant) |
            DQ(numero_documento__icontains=q_mant)
        )
    if estado_mant:
        personal_mant_qs = personal_mant_qs.filter(estado=estado_mant)
    if cargo_mant:
        personal_mant_qs = personal_mant_qs.filter(
            DQ(cargo__icontains=cargo_mant) |
            DQ(especialidad__icontains=cargo_mant)
        )

    total_tecnicos = personal_mant_qs.count()
    paginator_mant = Paginator(personal_mant_qs, 15)
    page_mant      = paginator_mant.get_page(request.GET.get('page_mant'))

    return render(request, 'usuarios/centro_control.html', {
        'title':            'Centro de Control - SENA',
        'usuarios':         page_obj.object_list,
        'pendientes':       pendientes,
        'total':            total,
        'activos':          activos,
        'pendientes_count': pendientes_count,
        'inactivos':        inactivos,
        'page_obj':         page_obj,
        'tipos_usuario':    tipos_usuario,
        'centros_lista':    centros_lista,
        'fichas_lista':     fichas_lista,
        'estado_choices':   Usuario.ESTADO_CHOICES,
        'cargo_choices':    Usuario.CARGO_CHOICES,
        'tipo_mant_id':     (TipoUsuario.objects.filter(nombre='Personal de Mantenimiento', activo=True).values_list('pk', flat=True).first() or ''),
        'form_search': {
            'q':               q,
            'estado_filter':   estado_filter,
            'programa_filter': programa_filter,
        },
        # Mantenimiento
        'personal_mantenimiento': page_mant.object_list,
        'page_mant':              page_mant,
        'q_mant':                 q_mant,
        'estado_mant':            estado_mant,
        'cargo_mant':             cargo_mant,
        'total_tecnicos':         total_tecnicos,
    })

@login_required
@require_POST
def admin_editar_usuario_ajax(request, pk):
    """Edición inline de usuario vía AJAX — solo staff."""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Sin permisos'}, status=403)

    usuario = get_object_or_404(Usuario, pk=pk)

    for campo in ['nombres', 'apellidos', 'telefono', 'cargo', 'especialidad']:
        valor = request.POST.get(campo, '').strip()
        if valor:
            setattr(usuario, campo, valor)

    # centro_formacion es FK — recibimos el ID
    centro_id = request.POST.get('centro_formacion', '').strip()
    if centro_id:
        from sistema.models import CentroFormacion
        try:
            usuario.centro_formacion = CentroFormacion.objects.get(pk=int(centro_id))
        except (ValueError, CentroFormacion.DoesNotExist):
            pass

    # ficha es FK — recibimos el ID (solo aplica a Aprendiz)
    ficha_id = request.POST.get('ficha', '').strip()
    if ficha_id:
        from sistema.models import Ficha
        try:
            usuario.ficha = Ficha.objects.get(pk=int(ficha_id))
        except (ValueError, Ficha.DoesNotExist):
            pass
    elif ficha_id == '':
        usuario.ficha = None

    email = request.POST.get('email', '').strip()
    if email:
        if Usuario.objects.exclude(pk=pk).filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Ya existe un usuario con ese email.'}, status=400)
        usuario.email = email

    nuevo_estado = request.POST.get('estado', '').strip()
    if nuevo_estado and nuevo_estado in dict(Usuario.ESTADO_CHOICES):
        usuario.estado = nuevo_estado
        if nuevo_estado == 'activo' and not usuario.fecha_aprobacion:
            usuario.fecha_aprobacion = timezone.now()

    tipo_usuario_id = request.POST.get('tipo_usuario_id', '').strip()
    if tipo_usuario_id:
        try:
            usuario.tipo_usuario = TipoUsuario.objects.get(pk=int(tipo_usuario_id), activo=True)
        except (TipoUsuario.DoesNotExist, ValueError):
            return JsonResponse({'success': False, 'message': 'Tipo de usuario no válido.'}, status=400)

    try:
        usuario.save()
        return JsonResponse({'success': True, 'message': f'Usuario {usuario.nombres} {usuario.apellidos} actualizado correctamente.'})
    except Exception as exc:
        return JsonResponse({'success': False, 'message': f'Error al guardar: {str(exc)}'}, status=500)

@login_required
@require_POST
def admin_crear_usuario_ajax(request):
    """Crea un nuevo usuario desde el Centro de Control — solo staff."""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Sin permisos.'}, status=403)

    # Recoger campos
    nombres          = request.POST.get('nombres', '').strip()
    apellidos        = request.POST.get('apellidos', '').strip()
    tipo_documento   = request.POST.get('tipo_documento', 'CC').strip()
    numero_documento = request.POST.get('numero_documento', '').strip()
    email            = request.POST.get('email', '').strip()
    telefono         = request.POST.get('telefono', '').strip()
    cargo            = request.POST.get('cargo', '').strip()
    especialidad     = request.POST.get('especialidad', '').strip()
    centro_id        = request.POST.get('centro_formacion', '').strip() or None
    ficha_id         = request.POST.get('ficha', '').strip() or None
    tipo_usuario_id  = request.POST.get('tipo_usuario_id', '').strip()
    password         = request.POST.get('password', '').strip()
    confirmar        = request.POST.get('confirmar_password', '').strip()

    # Validaciones básicas
    if not all([nombres, apellidos, numero_documento, email, password]):
        return JsonResponse({'success': False, 'message': 'Faltan campos obligatorios.'}, status=400)

    if password != confirmar:
        return JsonResponse({'success': False, 'message': 'Las contraseñas no coinciden.'}, status=400)

    if len(password) < 8:
        return JsonResponse({'success': False, 'message': 'La contraseña debe tener al menos 8 caracteres.'}, status=400)

    if Usuario.objects.filter(numero_documento=numero_documento).exists():
        return JsonResponse({'success': False, 'message': 'Ya existe un usuario con ese número de documento.'}, status=400)

    if Usuario.objects.filter(email=email).exists():
        return JsonResponse({'success': False, 'message': 'Ya existe un usuario con ese email.'}, status=400)

    if User.objects.filter(username=numero_documento).exists():
        return JsonResponse({'success': False, 'message': 'Ya existe una cuenta con ese número de documento.'}, status=400)

    try:
        tipo_usuario_id = int(tipo_usuario_id)
        tipo_usuario = TipoUsuario.objects.get(pk=tipo_usuario_id)
    except (ValueError, TipoUsuario.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'Tipo de usuario no válido.'}, status=400)

    try:
        # Crear usuario Django (hashea con PBKDF2 automáticamente)
        django_user = User.objects.create_user(
            username=numero_documento,
            email=email,
            password=password,
        )

        from sistema.models import CentroFormacion as CF, Ficha as F
        centro_obj = None
        if centro_id:
            try:
                centro_obj = CF.objects.get(pk=int(centro_id))
            except (ValueError, CF.DoesNotExist):
                pass
        ficha_obj = None
        if ficha_id:
            try:
                ficha_obj = F.objects.get(pk=int(ficha_id))
            except (ValueError, F.DoesNotExist):
                pass

        usuario = Usuario.objects.create(
            nombres=nombres,
            apellidos=apellidos,
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
            email=email,
            telefono=telefono,
            cargo=cargo,
            especialidad=especialidad,
            centro_formacion=centro_obj,
            ficha=ficha_obj,
            tipo_usuario=tipo_usuario,
            estado='activo',
            fecha_aprobacion=timezone.now(),
        )

        # Enviar correo de bienvenida
        try:
            contexto_email = {
                'nombres': usuario.nombres,
                'apellidos': usuario.apellidos,
                'numero_documento': usuario.numero_documento,
                'email': usuario.email,
                'cargo': usuario.cargo,
                'fecha_registro': timezone.now().strftime('%d/%m/%Y %H:%M'),
            }
            html_message = render_to_string('usuarios/email_bienvenida.html', contexto_email)
            send_mail(
                subject='✅ Tu cuenta en SENA Maquinaria fue creada exitosamente',
                message=strip_tags(html_message),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception:
            pass

        return JsonResponse({
            'success': True,
            'message': f'Usuario {usuario.nombre_completo} creado correctamente.',
            'usuario': {
                'pk': usuario.pk,
                'nombre_completo': usuario.nombre_completo,
                'numero_documento': usuario.numero_documento,
                'cargo': usuario.cargo,
                'estado': usuario.estado,
                'iniciales': usuario.iniciales,
                'email': usuario.email,
                'especialidad': usuario.especialidad,
                'centro_formacion': usuario.centro_formacion,
                'tipo_usuario_id': usuario.tipo_usuario_id,
                'tipo_documento_display': usuario.get_tipo_documento_display(),
                'telefono': usuario.telefono,
                'apellidos': usuario.apellidos,
                'nombres': usuario.nombres,
            }
        })

    except Exception as exc:
        return JsonResponse({'success': False, 'message': f'Error al crear usuario: {str(exc)}'}, status=500)


@login_required
@require_POST
def admin_cambiar_password_ajax(request, pk):
    """Cambia la contraseña de un usuario — solo staff."""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Sin permisos.'}, status=403)

    usuario = get_object_or_404(Usuario, pk=pk)
    nueva_password   = request.POST.get('nueva_password', '').strip()
    confirmar        = request.POST.get('confirmar_password', '').strip()

    if not nueva_password:
        return JsonResponse({'success': False, 'message': 'La contraseña no puede estar vacía.'}, status=400)

    if nueva_password != confirmar:
        return JsonResponse({'success': False, 'message': 'Las contraseñas no coinciden.'}, status=400)

    if len(nueva_password) < 8:
        return JsonResponse({'success': False, 'message': 'La contraseña debe tener al menos 8 caracteres.'}, status=400)

    try:
        django_user = User.objects.get(username=usuario.numero_documento)
        django_user.set_password(nueva_password)  # PBKDF2-SHA256
        django_user.save()
        return JsonResponse({'success': True, 'message': f'Contraseña de {usuario.nombre_completo} actualizada correctamente.'})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'No se encontró la cuenta de autenticación del usuario.'}, status=404)
    except Exception as exc:
        return JsonResponse({'success': False, 'message': f'Error: {str(exc)}'}, status=500)


@login_required
def configuracion_view(request):
    """Vista de configuración general de usuarios"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página')
        return redirect('usuarios:dashboard')

    # Estadísticas
    stats = {
        'total_usuarios': Usuario.objects.count(),
        'usuarios_activos': Usuario.objects.filter(estado='activo').count(),
        'usuarios_pendientes': Usuario.objects.filter(estado='pendiente').count(),
        'sesiones_activas': SesionUsuario.objects.filter(activa=True).count(),
    }

    return render(request, 'usuarios/configuracion.html', {
        'stats': stats,
        'title': 'Configuración Usuarios - SENA'
    })

@login_required
def cambiar_password_view(request):
    """Vista para cambiar contraseña"""
    form = CambiarPasswordForm(user=request.user)
    if request.method == 'POST':
        form = CambiarPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            nueva_password = form.cleaned_data.get('password_nueva')
            request.user.set_password(nueva_password)
            request.user.save()
            messages.success(request, 'Contraseña cambiada correctamente')
            return redirect('usuarios:perfil')

    return render(request, 'usuarios/cambiar_password.html', {
        'form': form,
        'title': 'Cambiar Contraseña - SENA'
    })

def register_view(request):
    """Vista de registro de usuarios - Solo para Instructores"""
    form = RegistroUsuarioForm()
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)

            # tipo_usuario viene directo del form; sincronizar cargo con el nombre del tipo
            tipo_usuario = form.cleaned_data.get('tipo_usuario')
            usuario.tipo_usuario = tipo_usuario
            usuario.cargo = tipo_usuario.nombre if tipo_usuario else ''
            usuario.estado = 'activo'
            usuario.fecha_aprobacion = timezone.now()

            # Crear usuario de Django para autenticación
            password = form.cleaned_data.get('password')
            django_user = User.objects.create_user(
                username=usuario.numero_documento,
                email=usuario.email,
                password=password
            )

            usuario.save()

            # Enviar correo de bienvenida
            try:
                contexto_email = {
                    'nombres': usuario.nombres,
                    'apellidos': usuario.apellidos,
                    'numero_documento': usuario.numero_documento,
                    'email': usuario.email,
                    'cargo': usuario.cargo,
                    'fecha_registro': timezone.now().strftime('%d/%m/%Y %H:%M'),
                }
                html_message = render_to_string('usuarios/email_bienvenida.html', contexto_email)
                plain_message = strip_tags(html_message)
                send_mail(
                    subject='✅ Tu cuenta en SENA Maquinaria fue creada exitosamente',
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[usuario.email],
                    html_message=html_message,
                    fail_silently=True,
                )
            except Exception:
                pass  # El registro no falla si el correo no se envía

            messages.success(request,
                'Registro exitoso. Hemos enviado un correo de confirmación a tu dirección de email.')
            return redirect('usuarios:login')

    return render(request, 'usuarios/register.html', {
        'form': form,
        'title': 'Registro de Instructor - SENA'
    })

# API Views para AJAX
@login_required
def buscar_usuarios_api(request):
    """API para buscar usuarios via AJAX"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})

    usuarios = Usuario.objects.filter(
        Q(nombres__icontains=query) |
        Q(apellidos__icontains=query) |
        Q(numero_documento__icontains=query) |
        Q(email__icontains=query)
    )[:10]

    results = []
    for usuario in usuarios:
        results.append({
            'id': usuario.id,
            'text': f"{usuario.nombre_completo} ({usuario.numero_documento})",
            'email': usuario.email,
            'estado': usuario.estado
        })

    return JsonResponse({'results': results})

@login_required
def estadisticas_usuarios_api(request):
    """API para estadísticas de usuarios"""
    stats = {
        'total': Usuario.objects.count(),
        'por_estado': dict(Usuario.objects.values_list('estado').annotate(count=Count('estado'))),
        'por_tipo': list(Usuario.objects.values('tipo_usuario__nombre').annotate(count=Count('tipo_usuario'))),
        'registros_mes': Usuario.objects.filter(
            fecha_registro__month=timezone.now().month
        ).count()
    }

    return JsonResponse(stats)

# Vistas de recuperación de contraseña
def recuperar_password_view(request):
    """Vista para solicitar recuperación de contraseña"""
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')

    form = RecuperarPasswordForm()
    if request.method == 'POST':
        form = RecuperarPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')

            try:
                usuario = Usuario.objects.get(email=email)

                # Generar token único
                token = secrets.token_urlsafe(32)

                # Crear token de recuperación con expiración de 1 hora
                token_recuperacion = TokenRecuperacionPassword.objects.create(
                    usuario=usuario,
                    token=token,
                    fecha_expiracion=timezone.now() + timedelta(hours=1),
                    ip_solicitud=request.META.get('REMOTE_ADDR', '')
                )

                # Construir URL de recuperación
                reset_url = request.build_absolute_uri(
                    f'/usuarios/reset-password/{token}/'
                )

                # Preparar correo
                subject = 'Recuperacion de Contrasena - SENA Maquinaria'
                html_message = render_to_string('usuarios/email_recuperacion.html', {
                    'usuario': usuario,
                    'reset_url': reset_url,
                    'expiracion': 1  # horas
                })
                plain_message = strip_tags(html_message)
                from_email = settings.DEFAULT_FROM_EMAIL
                to_email = usuario.email

                # Enviar correo
                try:
                    from django.core.mail import EmailMultiAlternatives

                    # Usar EmailMultiAlternatives para mejor manejo de caracteres especiales
                    msg = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_message,
                        from_email=from_email,
                        to=[to_email]
                    )
                    msg.attach_alternative(html_message, "text/html")
                    msg.send()

                    messages.success(request,
                        'Se ha enviado un enlace de recuperacion a tu correo electronico.')
                except Exception as e:
                    messages.warning(request,
                        f'Se genero el token pero hubo un problema al enviar el correo: {str(e)}. '
                        f'Token: {token} (valido por 1 hora)')

            except Usuario.DoesNotExist:
                # Por seguridad, no revelar si el correo existe o no
                messages.success(request,
                    'Si el correo está registrado, recibirás un enlace de recuperación.')

            return redirect('usuarios:login')

    return render(request, 'usuarios/recuperar_password.html', {
        'form': form,
        'title': 'Recuperar Contraseña - SENA'
    })

def reset_password_view(request, token):
    """Vista para restablecer contraseña con token"""
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')

    try:
        token_obj = TokenRecuperacionPassword.objects.get(token=token)

        if not token_obj.es_valido():
            messages.error(request, 'El enlace de recuperación ha expirado o ya fue utilizado.')
            return redirect('usuarios:recuperar_password')

        form = ResetPasswordForm()
        if request.method == 'POST':
            form = ResetPasswordForm(request.POST)
            if form.is_valid():
                nueva_password = form.cleaned_data.get('password')

                # Obtener el usuario de Django asociado
                try:
                    user = User.objects.get(username=token_obj.usuario.numero_documento)
                    user.set_password(nueva_password)
                    user.save()

                    # Marcar token como usado
                    token_obj.usado = True
                    token_obj.save()

                    messages.success(request,
                        'Tu contraseña ha sido actualizada correctamente. Ya puedes iniciar sesión.')
                    return redirect('usuarios:login')

                except User.DoesNotExist:
                    messages.error(request, 'Error al actualizar la contraseña. Usuario no encontrado.')

        return render(request, 'usuarios/reset_password.html', {
            'form': form,
            'token': token,
            'usuario': token_obj.usuario,
            'title': 'Restablecer Contraseña - SENA'
        })

    except TokenRecuperacionPassword.DoesNotExist:
        messages.error(request, 'Enlace de recuperación inválido.')
        return redirect('usuarios:recuperar_password')


# ========================================
# VISTAS DE RECONOCIMIENTO FACIAL
# ========================================

def get_client_ip(request):
    """Obtiene la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
def registrar_rostro_page_view(request):
    """Página dedicada para registrar/actualizar el rostro del usuario."""
    try:
        usuario = Usuario.objects.get(numero_documento=request.user.username)
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('usuarios:perfil')

    tiene_reconocimiento_facial = ReconocimientoFacial.objects.filter(usuario=usuario, activo=True).exists()

    return render(request, 'usuarios/registrar_rostro.html', {
        'usuario': usuario,
        'tiene_reconocimiento_facial': tiene_reconocimiento_facial,
        'title': 'Registro Facial - SENA',
    })


@require_POST
@csrf_exempt  # TODO: Remover en producción, usar CSRF token correctamente
def registrar_rostro_view(request):
    """
    API endpoint para registrar el rostro de un usuario.
    Usado tanto en registro como para actualizar rostro de usuario existente.
    """
    try:
        # Verificar autenticación
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Debe estar autenticado'
            }, status=401)

        # Obtener imagen en base64
        data = json.loads(request.body)
        imagen_base64 = data.get('imagen')

        if not imagen_base64:
            return JsonResponse({
                'success': False,
                'error': 'No se recibió imagen'
            }, status=400)

        # Decodificar imagen
        imagen = facial_service.decode_base64_image(imagen_base64)
        if imagen is None:
            return JsonResponse({
                'success': False,
                'error': 'Error decodificando imagen'
            }, status=400)

        # Validar calidad
        calidad_ok, mensaje_calidad = facial_service.validar_calidad_imagen(imagen)
        if not calidad_ok:
            return JsonResponse({
                'success': False,
                'error': mensaje_calidad
            }, status=400)

        # Extraer embedding
        exito, embedding, mensaje = facial_service.extraer_embedding(imagen)

        if not exito:
            return JsonResponse({
                'success': False,
                'error': mensaje
            }, status=400)

        # Obtener usuario
        try:
            usuario = Usuario.objects.get(numero_documento=request.user.username)
        except Usuario.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Usuario no encontrado'
            }, status=404)

        # Guardar o actualizar reconocimiento facial
        reconocimiento, created = ReconocimientoFacial.objects.update_or_create(
            usuario=usuario,
            defaults={
                'embedding': embedding,
                'confianza_registro': 0.95,  # Placeholder, ajustar según necesidad
                'activo': True,
                'ip_registro': get_client_ip(request),
                'user_agent_registro': request.META.get('HTTP_USER_AGENT', '')
            }
        )

        # Registrar intento exitoso
        IntentoReconocimientoFacial.objects.create(
            usuario=usuario,
            tipo_intento='registro' if created else 'actualizacion',
            resultado='exitoso',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        return JsonResponse({
            'success': True,
            'message': 'Rostro registrado correctamente' if created else 'Rostro actualizado correctamente'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Datos JSON inválidos'
        }, status=400)
    except Exception as e:
        logger.error(f"Error en registro de rostro: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, status=500)


@require_POST
@csrf_exempt  # TODO: Remover en producción
def login_facial_view(request):
    """
    API endpoint para autenticación mediante reconocimiento facial.
    """
    try:
        # Obtener datos
        data = json.loads(request.body)
        numero_documento = data.get('numero_documento')
        imagen_base64 = data.get('imagen')

        if not numero_documento or not imagen_base64:
            return JsonResponse({
                'success': False,
                'error': 'Faltan datos requeridos'
            }, status=400)

        # Rate limiting por IP
        ip_cliente = get_client_ip(request)
        rate_limit_key = f'facial_login_attempts_{ip_cliente}'
        intentos = cache.get(rate_limit_key, 0)

        if intentos >= RATE_LIMIT_FACIAL_LOGIN:
            return JsonResponse({
                'success': False,
                'error': f'Demasiados intentos. Intente nuevamente en {RATE_LIMIT_WINDOW // 60} minutos'
            }, status=429)

        # Incrementar contador
        cache.set(rate_limit_key, intentos + 1, RATE_LIMIT_WINDOW)

        # Buscar usuario
        try:
            usuario = Usuario.objects.get(numero_documento=numero_documento)
        except Usuario.DoesNotExist:
            # Registrar intento fallido sin revelar que el usuario no existe
            IntentoReconocimientoFacial.objects.create(
                usuario=None,
                tipo_intento='login',
                resultado='fallido',
                mensaje_error='Usuario no encontrado',
                ip_address=ip_cliente,
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            return JsonResponse({
                'success': False,
                'error': 'Credenciales inválidas'
            }, status=401)

        # Verificar si tiene reconocimiento facial activo
        try:
            reconocimiento = ReconocimientoFacial.objects.get(
                usuario=usuario,
                activo=True
            )
        except ReconocimientoFacial.DoesNotExist:
            IntentoReconocimientoFacial.objects.create(
                usuario=usuario,
                tipo_intento='login',
                resultado='fallido',
                mensaje_error='Reconocimiento facial no configurado',
                ip_address=ip_cliente,
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            return JsonResponse({
                'success': False,
                'error': 'Reconocimiento facial no configurado para este usuario'
            }, status=400)

        # Verificar estado del usuario
        if usuario.estado != 'activo':
            IntentoReconocimientoFacial.objects.create(
                usuario=usuario,
                tipo_intento='login',
                resultado='fallido',
                mensaje_error=f'Usuario en estado: {usuario.estado}',
                ip_address=ip_cliente,
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            return JsonResponse({
                'success': False,
                'error': f'Usuario {usuario.get_estado_display()}'
            }, status=403)

        # Decodificar y validar imagen
        imagen = facial_service.decode_base64_image(imagen_base64)
        if imagen is None:
            return JsonResponse({
                'success': False,
                'error': 'Error decodificando imagen'
            }, status=400)

        # Validar calidad
        calidad_ok, mensaje_calidad = facial_service.validar_calidad_imagen(imagen)
        if not calidad_ok:
            return JsonResponse({
                'success': False,
                'error': mensaje_calidad
            }, status=400)

        # Extraer embedding
        exito, embedding_capturado, mensaje = facial_service.extraer_embedding(imagen)
        if not exito:
            IntentoReconocimientoFacial.objects.create(
                usuario=usuario,
                tipo_intento='login',
                resultado='error',
                mensaje_error=mensaje,
                ip_address=ip_cliente,
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            return JsonResponse({
                'success': False,
                'error': mensaje
            }, status=400)

        # Verificar autenticación
        autenticado, similitud, mensaje_auth = facial_service.verificar_autenticacion(
            embedding_capturado,
            reconocimiento.embedding
        )

        # Registrar intento
        IntentoReconocimientoFacial.objects.create(
            usuario=usuario,
            tipo_intento='login',
            resultado='exitoso' if autenticado else 'fallido',
            similitud=similitud,
            mensaje_error='' if autenticado else mensaje_auth,
            ip_address=ip_cliente,
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        if not autenticado:
            return JsonResponse({
                'success': False,
                'error': 'Rostro no coincide con el registrado'
            }, status=401)

        # AUTENTICACIÓN EXITOSA
        # Crear sesión de Django
        django_user = User.objects.get(username=numero_documento)
        django_user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, django_user)

        # Registrar sesión en SesionUsuario
        SesionUsuario.objects.create(
            usuario=usuario,
            token_sesion=request.session.session_key or '',
            ip_address=ip_cliente,
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        # Actualizar último acceso
        usuario.ultimo_acceso = timezone.now()
        usuario.save()

        # Limpiar rate limit en caso de éxito
        cache.delete(rate_limit_key)

        return JsonResponse({
            'success': True,
            'message': 'Autenticación exitosa',
            'similitud': round(similitud * 100, 2),
            'redirect_url': '/usuarios/dashboard/'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Datos JSON inválidos'
        }, status=400)
    except Exception as e:
        logger.error(f"Error en login facial: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=500)


@login_required
def verificar_tiene_reconocimiento_facial(request):
    """
    API endpoint para verificar si el usuario tiene reconocimiento facial activo.
    """
    try:
        usuario = Usuario.objects.get(numero_documento=request.user.username)
        tiene_reconocimiento = ReconocimientoFacial.objects.filter(
            usuario=usuario,
            activo=True
        ).exists()

        return JsonResponse({
            'tiene_reconocimiento': tiene_reconocimiento
        })
    except Usuario.DoesNotExist:
        return JsonResponse({
            'tiene_reconocimiento': False
        }, status=404)


@login_required
@require_POST
def eliminar_reconocimiento_facial(request):
    """
    Permite al usuario eliminar su reconocimiento facial.
    """
    try:
        usuario = Usuario.objects.get(numero_documento=request.user.username)
        reconocimiento = ReconocimientoFacial.objects.get(usuario=usuario)
        reconocimiento.activo = False
        reconocimiento.save()

        return JsonResponse({
            'success': True,
            'message': 'Reconocimiento facial desactivado'
        })
    except (Usuario.DoesNotExist, ReconocimientoFacial.DoesNotExist):
        return JsonResponse({
            'success': False,
            'error': 'No se encontró reconocimiento facial activo'
        }, status=404)
