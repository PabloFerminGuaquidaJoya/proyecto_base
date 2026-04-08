# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, FileResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.db import connection
from .models import BackupDatabase, LogActividad, CentroFormacion, AmbienteFormacion
from django.views.decorators.http import require_POST
from usuarios.models import Usuario
import os
import subprocess
import sys
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


# ==================== UTILIDADES MySQL ====================

# Rutas comunes donde MySQL instala sus herramientas en Windows
_MYSQL_BIN_PATHS_WINDOWS = [
    r'C:\Program Files\MySQL\MySQL Server 9.5\bin',
    r'C:\Program Files\MySQL\MySQL Server 9.3\bin',
    r'C:\Program Files\MySQL\MySQL Server 9.0\bin',
    r'C:\Program Files\MySQL\MySQL Server 8.4\bin',
    r'C:\Program Files\MySQL\MySQL Server 8.0\bin',
    r'C:\Program Files\MySQL\MySQL Server 5.7\bin',
    r'C:\xampp\mysql\bin',
    r'C:\wamp64\bin\mysql\mysql8.0\bin',
    r'C:\wamp\bin\mysql\mysql8.0\bin',
    r'C:\laragon\bin\mysql\mysql-8.0\bin',
]


def _encontrar_ejecutable(nombre):
    """
    Busca el ejecutable de MySQL (mysqldump o mysql) en el PATH y en rutas
    comunes de instalación de Windows. Retorna la ruta completa o el nombre
    simple si está en el PATH.
    """
    import shutil
    import platform

    # Primero intentar directamente (si está en el PATH del sistema)
    if shutil.which(nombre):
        return nombre

    # En Windows, buscar en rutas comunes de instalación de MySQL
    if platform.system() == 'Windows':
        exe = nombre + '.exe'
        # También buscar dinámicamente en C:\Program Files\MySQL\
        base = r'C:\Program Files\MySQL'
        if os.path.isdir(base):
            for entry in sorted(os.listdir(base), reverse=True):
                candidate = os.path.join(base, entry, 'bin', exe)
                if os.path.isfile(candidate):
                    return candidate

        for path in _MYSQL_BIN_PATHS_WINDOWS:
            candidate = os.path.join(path, exe)
            if os.path.isfile(candidate):
                return candidate

    return None  # No encontrado


def _get_db_config():
    """Obtiene la configuración de la base de datos MySQL desde settings."""
    db = settings.DATABASES['default']
    return {
        'name': db['NAME'],
        'user': db['USER'],
        'password': db['PASSWORD'],
        'host': db.get('HOST', 'localhost'),
        'port': db.get('PORT', '3306'),
    }


def _contar_tablas_y_registros():
    """Cuenta las tablas y registros totales en la base de datos MySQL."""
    total_tablas = 0
    total_registros = 0
    try:
        with connection.cursor() as cursor:
            db_name = settings.DATABASES['default']['NAME']
            cursor.execute(
                "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
                "WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE'",
                [db_name]
            )
            tablas = cursor.fetchall()
            total_tablas = len(tablas)

            for (tabla_nombre,) in tablas:
                cursor.execute(
                    "SELECT TABLE_ROWS FROM INFORMATION_SCHEMA.TABLES "
                    "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s",
                    [db_name, tabla_nombre]
                )
                row = cursor.fetchone()
                if row and row[0]:
                    total_registros += row[0]
    except Exception as e:
        logger.error(f"Error contando tablas/registros MySQL: {e}")

    return total_tablas, total_registros


def _obtener_tamano_db():
    """Obtiene el tamaño de la base de datos MySQL en MB."""
    try:
        with connection.cursor() as cursor:
            db_name = settings.DATABASES['default']['NAME']
            cursor.execute(
                "SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS size_mb "
                "FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %s",
                [db_name]
            )
            row = cursor.fetchone()
            return float(row[0]) if row and row[0] else 0.0
    except Exception as e:
        logger.error(f"Error obteniendo tamaño de BD MySQL: {e}")
        return 0.0


def _ejecutar_mysqldump(backup_path):
    """
    Ejecuta mysqldump para crear un backup SQL de la base de datos.
    Retorna (exito: bool, mensaje: str).
    """
    db = _get_db_config()

    mysqldump_exe = _encontrar_ejecutable('mysqldump')
    if not mysqldump_exe:
        return False, (
            'mysqldump no encontrado. Instale MySQL y asegúrese de que '
            'C:\\Program Files\\MySQL\\MySQL Server X.X\\bin esté en el PATH del sistema.'
        )

    cmd = [
        mysqldump_exe,
        f'--user={db["user"]}',
        f'--password={db["password"]}',
        f'--host={db["host"]}',
        f'--port={db["port"]}',
        '--single-transaction',
        '--routines',
        '--triggers',
        '--add-drop-table',
        '--set-charset',
        '--default-character-set=utf8mb4',
        db['name'],
    ]

    try:
        with open(backup_path, 'w', encoding='utf-8') as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                timeout=300,
            )

        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='replace').strip()
            # Filtrar warnings de contraseña (no son errores reales)
            lineas_error = [
                l for l in error_msg.splitlines()
                if 'error' in l.lower() and 'using a password' not in l.lower()
            ]
            if lineas_error:
                return False, f'Error en mysqldump: {chr(10).join(lineas_error)}'

        return True, 'Backup creado exitosamente'

    except subprocess.TimeoutExpired:
        return False, 'El proceso de backup excedió el tiempo límite (5 minutos).'
    except Exception as e:
        return False, f'Error ejecutando mysqldump: {str(e)}'


def _ejecutar_mysql_restore(backup_path):
    """
    Ejecuta mysql para restaurar un backup SQL.
    Retorna (exito: bool, mensaje: str).
    """
    db = _get_db_config()

    mysql_exe = _encontrar_ejecutable('mysql')
    if not mysql_exe:
        return False, (
            'mysql no encontrado. Instale MySQL y asegúrese de que '
            'C:\\Program Files\\MySQL\\MySQL Server X.X\\bin esté en el PATH del sistema.'
        )

    cmd = [
        mysql_exe,
        f'--user={db["user"]}',
        f'--password={db["password"]}',
        f'--host={db["host"]}',
        f'--port={db["port"]}',
        '--default-character-set=utf8mb4',
        db['name'],
    ]

    try:
        with open(backup_path, 'r', encoding='utf-8') as f:
            result = subprocess.run(
                cmd,
                stdin=f,
                stderr=subprocess.PIPE,
                timeout=600,
            )

        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='replace').strip()
            lineas_error = [
                l for l in error_msg.splitlines()
                if 'error' in l.lower() and 'using a password' not in l.lower()
            ]
            if lineas_error:
                return False, f'Error en restauración MySQL: {chr(10).join(lineas_error)}'

        return True, 'Base de datos restaurada exitosamente'

    except subprocess.TimeoutExpired:
        return False, 'El proceso de restauración excedió el tiempo límite (10 minutos).'
    except Exception as e:
        return False, f'Error ejecutando restauración: {str(e)}'


def _obtener_usuario_actual(request):
    """Obtiene el Usuario del modelo personalizado a partir del request."""
    try:
        return Usuario.objects.get(numero_documento=request.user.username)
    except Usuario.DoesNotExist:
        return None


# ==================== ERROR HANDLERS ====================

def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    return render(request, 'errors/500.html', status=500)


# ==================== STATUS CHECKS ====================

def status_check(request):
    return JsonResponse({
        'status': 'ok',
        'timestamp': timezone.now().isoformat(),
        'service': 'Sistema SENA - Gestion Maquinaria'
    })

def health_check(request):
    db_status = 'connected'
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        db_status = 'disconnected'

    return JsonResponse({
        'status': 'healthy' if db_status == 'connected' else 'unhealthy',
        'timestamp': timezone.now().isoformat(),
        'database': db_status,
        'database_engine': 'MySQL',
        'version': '1.0.0'
    })

def version_info(request):
    return JsonResponse({
        'version': '1.0.0',
        'build': 'prototype',
        'database_engine': 'MySQL',
        'timestamp': timezone.now().isoformat()
    })

def database_status(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
        return JsonResponse({
            'status': 'connected',
            'engine': 'MySQL',
            'version': version,
            'database': settings.DATABASES['default']['NAME'],
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)


# ==================== PERMISOS ====================

def es_administrador(user):
    """Verifica si el usuario es administrador"""
    try:
        return user.tipo_usuario and user.tipo_usuario.nombre == 'Administrador'
    except Exception:
        return False


# ==================== VISTAS DE BACKUP (MySQL) ====================

@login_required
def gestionar_backups(request):
    """Vista principal para gestionar backups"""
    backups = BackupDatabase.objects.all().order_by('-fecha_creacion')

    # Información de la base de datos MySQL
    db_name = settings.DATABASES['default']['NAME']
    db_size = _obtener_tamano_db()
    total_tablas, total_registros = _contar_tablas_y_registros()

    context = {
        'backups': backups,
        'db_size': db_size,
        'total_registros': total_registros,
        'total_tablas': total_tablas,
        'db_path': f'MySQL: {db_name}',
    }

    return render(request, 'sistema/gestionar_backups.html', context)


@login_required
def crear_backup(request):
    """Crear un nuevo backup de la base de datos MySQL usando mysqldump"""
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre', f'Backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
            descripcion = request.POST.get('descripcion', '')
            usuario_actual = _obtener_usuario_actual(request)

            # Crear el registro del backup
            backup = BackupDatabase.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                tipo='manual',
                creado_por=usuario_actual,
                estado='creando',
                version_django=settings.VERSION if hasattr(settings, 'VERSION') else '5.2.6',
                version_python=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            )

            # Crear directorio de backups si no existe
            backup_dir = os.path.join(
                settings.MEDIA_ROOT, 'backups',
                datetime.now().strftime('%Y'),
                datetime.now().strftime('%m')
            )
            os.makedirs(backup_dir, exist_ok=True)

            # Nombre del archivo de backup (.sql para MySQL)
            backup_filename = f'backup_{backup.id}.sql'
            backup_path = os.path.join(backup_dir, backup_filename)

            # Ejecutar mysqldump
            exito, mensaje = _ejecutar_mysqldump(backup_path)

            if not exito:
                backup.estado = 'error'
                backup.metadatos = {'error': mensaje}
                backup.save()
                messages.error(request, f'Error al crear backup: {mensaje}')
                return redirect('sistema:gestionar_backups')

            # Obtener tamaño del archivo generado
            tamaño = os.path.getsize(backup_path) if os.path.exists(backup_path) else 0

            # Contar tablas y registros
            total_tablas, total_registros = _contar_tablas_y_registros()

            # Actualizar el backup
            backup.ruta_archivo = backup_path
            backup.tamaño_bytes = tamaño
            backup.total_tablas = total_tablas
            backup.total_registros = total_registros
            backup.estado = 'completado'
            backup.fecha_completado = timezone.now()
            backup.metadatos = {
                'engine': 'MySQL',
                'database': settings.DATABASES['default']['NAME'],
                'host': settings.DATABASES['default'].get('HOST', 'localhost'),
            }
            backup.save()

            # Registrar en log
            LogActividad.objects.create(
                usuario=usuario_actual,
                modulo='backups',
                nivel='info',
                accion='crear_backup',
                descripcion=f'Backup MySQL creado: {nombre}',
                objeto_tipo='BackupDatabase',
                objeto_id=str(backup.id)
            )

            messages.success(request, f'Backup "{nombre}" creado exitosamente. Tamaño: {backup.tamaño_mb} MB')
            return redirect('sistema:gestionar_backups')

        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            messages.error(request, f'Error al crear backup: {str(e)}')
            if 'backup' in locals():
                backup.estado = 'error'
                backup.save()
            return redirect('sistema:gestionar_backups')

    return render(request, 'sistema/crear_backup.html')


@login_required
def restaurar_backup(request, backup_id):
    """Restaurar la base de datos MySQL desde un backup .sql"""
    backup = get_object_or_404(BackupDatabase, id=backup_id)

    if request.method == 'POST':
        if not backup.puede_restaurar:
            messages.error(request, 'Este backup no puede ser restaurado.')
            return redirect('sistema:gestionar_backups')

        usuario_actual = _obtener_usuario_actual(request)

        try:
            # Crear un backup de seguridad antes de restaurar
            pre_restore_dir = os.path.join(
                settings.MEDIA_ROOT, 'backups', 'pre_restore'
            )
            os.makedirs(pre_restore_dir, exist_ok=True)
            pre_restore_path = os.path.join(
                pre_restore_dir,
                f'pre_restore_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sql'
            )

            exito_pre, msg_pre = _ejecutar_mysqldump(pre_restore_path)
            if not exito_pre:
                messages.error(
                    request,
                    f'No se pudo crear backup de seguridad previo: {msg_pre}. '
                    f'Restauración cancelada por seguridad.'
                )
                return redirect('sistema:gestionar_backups')

            # Actualizar estado del backup
            backup.estado = 'restaurando'
            backup.save()

            # Restaurar el backup
            if os.path.exists(backup.ruta_archivo):
                exito, mensaje = _ejecutar_mysql_restore(backup.ruta_archivo)

                if not exito:
                    # Intentar restaurar el backup de seguridad
                    messages.error(request, f'Error al restaurar: {mensaje}')
                    exito_rollback, _ = _ejecutar_mysql_restore(pre_restore_path)
                    if exito_rollback:
                        messages.warning(request, 'Se restauró la base de datos al estado anterior.')
                    else:
                        messages.error(
                            request,
                            f'No se pudo revertir. Backup de seguridad disponible en: {pre_restore_path}'
                        )
                    backup.estado = 'error'
                    backup.save()
                    return redirect('sistema:gestionar_backups')

                # Actualizar el registro del backup
                backup.estado = 'restaurado'
                backup.fecha_restauracion = timezone.now()
                backup.restaurado_por = usuario_actual
                backup.notas_restauracion = request.POST.get('notas', '')
                backup.save()

                # Registrar en log
                LogActividad.objects.create(
                    usuario=usuario_actual,
                    modulo='backups',
                    nivel='warning',
                    accion='restaurar_backup',
                    descripcion=f'Base de datos MySQL restaurada desde: {backup.nombre}',
                    objeto_tipo='BackupDatabase',
                    objeto_id=str(backup.id)
                )

                messages.success(
                    request,
                    f'Base de datos restaurada exitosamente desde "{backup.nombre}". '
                    f'Backup de seguridad previo en: {pre_restore_path}'
                )
                return redirect('sistema:gestionar_backups')
            else:
                messages.error(request, 'El archivo de backup no existe.')
                backup.estado = 'error'
                backup.save()
                return redirect('sistema:gestionar_backups')

        except Exception as e:
            logger.error(f"Error restaurando backup: {e}")
            messages.error(request, f'Error al restaurar backup: {str(e)}')
            backup.estado = 'error'
            backup.save()
            return redirect('sistema:gestionar_backups')

    context = {
        'backup': backup
    }
    return render(request, 'sistema/confirmar_restaurar.html', context)


@login_required
def descargar_backup(request, backup_id):
    """Descargar un archivo de backup MySQL (.sql)"""
    backup = get_object_or_404(BackupDatabase, id=backup_id)
    usuario_actual = _obtener_usuario_actual(request)

    if backup.estado == 'completado' and backup.ruta_archivo and os.path.exists(backup.ruta_archivo):
        try:
            # Registrar descarga en log
            LogActividad.objects.create(
                usuario=usuario_actual,
                modulo='backups',
                nivel='info',
                accion='descargar_backup',
                descripcion=f'Backup descargado: {backup.nombre}',
                objeto_tipo='BackupDatabase',
                objeto_id=str(backup.id)
            )

            response = FileResponse(
                open(backup.ruta_archivo, 'rb'),
                content_type='application/sql'
            )
            response['Content-Disposition'] = f'attachment; filename="{backup.nombre}.sql"'
            return response
        except Exception as e:
            messages.error(request, f'Error al descargar backup: {str(e)}')
            return redirect('sistema:gestionar_backups')
    else:
        messages.error(request, 'El backup no está disponible para descarga.')
        return redirect('sistema:gestionar_backups')


@login_required
def eliminar_backup(request, backup_id):
    """Eliminar un backup"""
    backup = get_object_or_404(BackupDatabase, id=backup_id)
    usuario_actual = _obtener_usuario_actual(request)

    if request.method == 'POST':
        nombre = backup.nombre
        ruta = backup.ruta_archivo

        try:
            # Eliminar el archivo físico
            if ruta and os.path.exists(ruta):
                try:
                    os.remove(ruta)
                except Exception as e:
                    messages.warning(request, f'No se pudo eliminar el archivo físico: {str(e)}')

            # Registrar en log antes de eliminar el registro
            LogActividad.objects.create(
                usuario=usuario_actual,
                modulo='backups',
                nivel='warning',
                accion='eliminar_backup',
                descripcion=f'Backup eliminado: {nombre}',
                objeto_tipo='BackupDatabase',
                objeto_id=str(backup.id)
            )

            # Eliminar el registro de la base de datos
            backup.delete()
            messages.success(request, f'Backup "{nombre}" eliminado exitosamente.')

        except Exception as e:
            messages.error(request, f'Error al eliminar backup: {str(e)}')

        return redirect('sistema:gestionar_backups')

    context = {
        'backup': backup
    }
    return render(request, 'sistema/confirmar_eliminar_backup.html', context)


@login_required
def detalle_backup(request, backup_id):
    """Ver detalles de un backup"""
    backup = get_object_or_404(BackupDatabase, id=backup_id)

    # Verificar si el archivo existe
    archivo_existe = os.path.exists(backup.ruta_archivo) if backup.ruta_archivo else False

    context = {
        'backup': backup,
        'archivo_existe': archivo_existe,
    }
    return render(request, 'sistema/detalle_backup.html', context)


@login_required
def crear_backup_rapido(request):
    """Crear backup rápido MySQL con un click (AJAX)"""
    if request.method == 'POST':
        try:
            usuario_actual = _obtener_usuario_actual(request)

            # Generar nombre automático con fecha y hora
            nombre = f'Backup_Rapido_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            descripcion = f'Copia de seguridad rápida creada desde {request.META.get("HTTP_REFERER", "sistema")}'

            # Crear el registro del backup
            backup = BackupDatabase.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                tipo='manual',
                creado_por=usuario_actual,
                estado='creando',
                version_django=settings.VERSION if hasattr(settings, 'VERSION') else '5.2.6',
                version_python=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            )

            # Crear directorio de backups si no existe
            backup_dir = os.path.join(
                settings.MEDIA_ROOT, 'backups',
                datetime.now().strftime('%Y'),
                datetime.now().strftime('%m')
            )
            os.makedirs(backup_dir, exist_ok=True)

            # Nombre del archivo de backup (.sql para MySQL)
            backup_filename = f'backup_{backup.id}.sql'
            backup_path = os.path.join(backup_dir, backup_filename)

            # Ejecutar mysqldump
            exito, mensaje = _ejecutar_mysqldump(backup_path)

            if not exito:
                backup.estado = 'error'
                backup.metadatos = {'error': mensaje}
                backup.save()
                return JsonResponse({
                    'success': False,
                    'message': f'Error al crear backup: {mensaje}'
                }, status=500)

            # Obtener tamaño del archivo
            tamaño = os.path.getsize(backup_path) if os.path.exists(backup_path) else 0

            # Contar tablas y registros
            total_tablas, total_registros = _contar_tablas_y_registros()

            # Actualizar el backup
            backup.ruta_archivo = backup_path
            backup.tamaño_bytes = tamaño
            backup.total_tablas = total_tablas
            backup.total_registros = total_registros
            backup.estado = 'completado'
            backup.fecha_completado = timezone.now()
            backup.metadatos = {
                'engine': 'MySQL',
                'database': settings.DATABASES['default']['NAME'],
                'host': settings.DATABASES['default'].get('HOST', 'localhost'),
            }
            backup.save()

            # Registrar en log
            LogActividad.objects.create(
                usuario=usuario_actual,
                modulo='backups',
                nivel='info',
                accion='crear_backup_rapido',
                descripcion=f'Backup rápido MySQL creado: {nombre}',
                objeto_tipo='BackupDatabase',
                objeto_id=str(backup.id)
            )

            return JsonResponse({
                'success': True,
                'message': f'Copia de seguridad creada exitosamente: {backup.tamaño_mb} MB',
                'backup_id': str(backup.id),
                'nombre': backup.nombre,
                'tamaño_mb': backup.tamaño_mb
            })

        except Exception as e:
            logger.error(f"Error en backup rápido: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error al crear backup: {str(e)}'
            }, status=500)

    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)


# ═══════════════════════════════════════════════════════════════════════
#  CENTRO ADMINISTRATIVO — Centros y Ambientes de Formación
# ═══════════════════════════════════════════════════════════════════════

def _solo_staff(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return False
    return True


@login_required
def centro_administrativo_view(request):
    """Vista principal del Centro Administrativo — solo staff."""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('usuarios:dashboard')

    centros   = CentroFormacion.objects.prefetch_related('ambientes').all()
    ambientes = AmbienteFormacion.objects.select_related('centro').all()

    return render(request, 'sistema/centro_administrativo.html', {
        'title':    'Centro Administrativo - SENA',
        'centros':  centros,
        'ambientes': ambientes,
        'total_centros':   centros.count(),
        'total_ambientes': ambientes.count(),
        'activos_centros': centros.filter(activo=True).count(),
        'activos_ambientes': ambientes.filter(activo=True).count(),
    })


# ── Centros ────────────────────────────────────────────────────────────

@login_required
@require_POST
def admin_crear_centro(request):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Sin permisos.'}, status=403)
    nombre = request.POST.get('nombre', '').strip()
    if not nombre:
        return JsonResponse({'success': False, 'message': 'El nombre es obligatorio.'}, status=400)
    if CentroFormacion.objects.filter(nombre__iexact=nombre).exists():
        return JsonResponse({'success': False, 'message': 'Ya existe un centro con ese nombre.'}, status=400)
    centro = CentroFormacion.objects.create(
        nombre      = nombre,
        codigo      = request.POST.get('codigo', '').strip(),
        direccion   = request.POST.get('direccion', '').strip(),
        telefono    = request.POST.get('telefono', '').strip(),
        email       = request.POST.get('email', '').strip(),
        descripcion = request.POST.get('descripcion', '').strip(),
        activo      = True,
    )
    return JsonResponse({'success': True, 'message': f'Centro "{centro.nombre}" creado.', 'id': centro.pk, 'nombre': centro.nombre})


@login_required
@require_POST
def admin_editar_centro(request, pk):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Sin permisos.'}, status=403)
    centro = get_object_or_404(CentroFormacion, pk=pk)
    nombre = request.POST.get('nombre', '').strip()
    if not nombre:
        return JsonResponse({'success': False, 'message': 'El nombre es obligatorio.'}, status=400)
    if CentroFormacion.objects.exclude(pk=pk).filter(nombre__iexact=nombre).exists():
        return JsonResponse({'success': False, 'message': 'Ya existe otro centro con ese nombre.'}, status=400)
    centro.nombre      = nombre
    centro.codigo      = request.POST.get('codigo', centro.codigo).strip()
    centro.direccion   = request.POST.get('direccion', centro.direccion).strip()
    centro.telefono    = request.POST.get('telefono', centro.telefono).strip()
    centro.email       = request.POST.get('email', centro.email).strip()
    centro.descripcion = request.POST.get('descripcion', centro.descripcion).strip()
    centro.activo      = request.POST.get('activo', 'true').lower() == 'true'
    centro.save()
    return JsonResponse({'success': True, 'message': f'Centro "{centro.nombre}" actualizado.'})


@login_required
@require_POST
def admin_eliminar_centro(request, pk):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Sin permisos.'}, status=403)
    centro = get_object_or_404(CentroFormacion, pk=pk)
    nombre = centro.nombre
    centro.delete()
    return JsonResponse({'success': True, 'message': f'Centro "{nombre}" eliminado.'})


# ── Ambientes ──────────────────────────────────────────────────────────

@login_required
@require_POST
def admin_crear_ambiente(request):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Sin permisos.'}, status=403)
    centro_id = request.POST.get('centro_id', '').strip()
    nombre    = request.POST.get('nombre', '').strip()
    if not nombre or not centro_id:
        return JsonResponse({'success': False, 'message': 'Centro y nombre son obligatorios.'}, status=400)
    centro = get_object_or_404(CentroFormacion, pk=centro_id)
    if AmbienteFormacion.objects.filter(centro=centro, nombre__iexact=nombre).exists():
        return JsonResponse({'success': False, 'message': 'Ya existe ese ambiente en este centro.'}, status=400)
    try:
        capacidad = int(request.POST.get('capacidad', 0))
    except ValueError:
        capacidad = 0
    ambiente = AmbienteFormacion.objects.create(
        centro      = centro,
        nombre      = nombre,
        codigo      = request.POST.get('codigo', '').strip(),
        capacidad   = capacidad,
        descripcion = request.POST.get('descripcion', '').strip(),
        activo      = True,
    )
    return JsonResponse({
        'success': True,
        'message': f'Ambiente "{ambiente.nombre}" creado en {centro.nombre}.',
        'id': ambiente.pk, 'nombre': ambiente.nombre, 'centro': centro.nombre,
    })


@login_required
@require_POST
def admin_editar_ambiente(request, pk):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Sin permisos.'}, status=403)
    ambiente  = get_object_or_404(AmbienteFormacion, pk=pk)
    nombre    = request.POST.get('nombre', '').strip()
    centro_id = request.POST.get('centro_id', '').strip()
    if not nombre:
        return JsonResponse({'success': False, 'message': 'El nombre es obligatorio.'}, status=400)
    if centro_id:
        ambiente.centro = get_object_or_404(CentroFormacion, pk=centro_id)
    try:
        ambiente.capacidad = int(request.POST.get('capacidad', ambiente.capacidad))
    except ValueError:
        pass
    ambiente.nombre      = nombre
    ambiente.codigo      = request.POST.get('codigo', ambiente.codigo).strip()
    ambiente.descripcion = request.POST.get('descripcion', ambiente.descripcion).strip()
    ambiente.activo      = request.POST.get('activo', 'true').lower() == 'true'
    ambiente.save()
    return JsonResponse({'success': True, 'message': f'Ambiente "{ambiente.nombre}" actualizado.'})


@login_required
@require_POST
def admin_eliminar_ambiente(request, pk):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Sin permisos.'}, status=403)
    ambiente = get_object_or_404(AmbienteFormacion, pk=pk)
    nombre   = ambiente.nombre
    ambiente.delete()
    return JsonResponse({'success': True, 'message': f'Ambiente "{nombre}" eliminado.'})
