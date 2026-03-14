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
            if nuevo_cargo:
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
            usuarios = usuarios.filter(centro_formacion__icontains=centro_formacion)

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

            # Asignar tipo de usuario según el cargo seleccionado
            cargo_seleccionado = form.cleaned_data.get('cargo', 'Instructor')
            tipo_usuario, created = TipoUsuario.objects.get_or_create(
                nombre=cargo_seleccionado,
                defaults={
                    'descripcion': f'{cargo_seleccionado} SENA',
                    'permisos': {},
                    'activo': True
                }
            )

            usuario.tipo_usuario = tipo_usuario
            usuario.estado = 'pendiente'

            # Crear usuario de Django para autenticación
            password = form.cleaned_data.get('password')
            django_user = User.objects.create_user(
                username=usuario.numero_documento,
                email=usuario.email,
                password=password
            )

            usuario.save()

            messages.success(request,
                'Registro exitoso como Instructor. Tu cuenta está pendiente de aprobación por un administrador.')
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
