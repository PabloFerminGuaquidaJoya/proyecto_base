# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, FileResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.db import connection
from .models import BackupDatabase, LogActividad
from usuarios.models import Usuario
import os
import shutil
import sys
from datetime import datetime

# Error handlers
def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    return render(request, 'errors/500.html', status=500)

# Status checks
def status_check(request):
    return JsonResponse({
        'status': 'ok',
        'timestamp': timezone.now().isoformat(),
        'service': 'Sistema SENA - Gestion Maquinaria'
    })

def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'database': 'connected',
        'version': '1.0.0'
    })

def version_info(request):
    return JsonResponse({
        'version': '1.0.0',
        'build': 'prototype',
        'timestamp': timezone.now().isoformat()
    })

def database_status(request):
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({'status': 'connected', 'timestamp': timezone.now().isoformat()})
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)

# Verificación de permisos de administrador
def es_administrador(user):
    """Verifica si el usuario es administrador"""
    try:
        return user.tipo_usuario and user.tipo_usuario.nombre == 'Administrador'
    except:
        return False

# ==================== VISTAS DE BACKUP ====================

@login_required
def gestionar_backups(request):
    """Vista principal para gestionar backups"""
    backups = BackupDatabase.objects.all().order_by('-fecha_creacion')

    # Información del sistema
    db_path = settings.DATABASES['default']['NAME']
    db_size = 0
    if os.path.exists(db_path):
        db_size = round(os.path.getsize(db_path) / (1024 * 1024), 2)

    # Contar registros en la base de datos
    total_registros = 0
    total_tablas = 0
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tablas = cursor.fetchall()
            total_tablas = len(tablas)

            for tabla in tablas:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla[0]}")
                count = cursor.fetchone()[0]
                total_registros += count
    except Exception as e:
        print(f"Error contando registros: {e}")

    context = {
        'backups': backups,
        'db_size': db_size,
        'total_registros': total_registros,
        'total_tablas': total_tablas,
        'db_path': db_path,
    }

    return render(request, 'sistema/gestionar_backups.html', context)

@login_required
def crear_backup(request):
    """Crear un nuevo backup de la base de datos"""
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre', f'Backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
            descripcion = request.POST.get('descripcion', '')

            # Obtener el usuario actual desde el modelo Usuario
            try:
                usuario_actual = Usuario.objects.get(numero_documento=request.user.username)
            except Usuario.DoesNotExist:
                usuario_actual = None

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

            # Ruta de la base de datos actual
            db_path = settings.DATABASES['default']['NAME']

            # Crear directorio de backups si no existe
            backup_dir = os.path.join(settings.MEDIA_ROOT, 'backups', datetime.now().strftime('%Y'), datetime.now().strftime('%m'))
            os.makedirs(backup_dir, exist_ok=True)

            # Nombre del archivo de backup
            backup_filename = f'backup_{backup.id}.db'
            backup_path = os.path.join(backup_dir, backup_filename)

            # Copiar la base de datos
            shutil.copy2(db_path, backup_path)

            # Obtener tamaño del archivo
            tamaño = os.path.getsize(backup_path)

            # Contar tablas y registros
            total_registros = 0
            total_tablas = 0
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                    tablas = cursor.fetchall()
                    total_tablas = len(tablas)

                    for tabla in tablas:
                        cursor.execute(f"SELECT COUNT(*) FROM {tabla[0]}")
                        count = cursor.fetchone()[0]
                        total_registros += count
            except Exception as e:
                print(f"Error contando: {e}")

            # Actualizar el backup
            backup.ruta_archivo = backup_path
            backup.tamaño_bytes = tamaño
            backup.total_tablas = total_tablas
            backup.total_registros = total_registros
            backup.estado = 'completado'
            backup.fecha_completado = timezone.now()
            backup.save()

            # Registrar en log
            LogActividad.objects.create(
                usuario=usuario_actual,
                modulo='backups',
                nivel='info',
                accion='crear_backup',
                descripcion=f'Backup creado: {nombre}',
                objeto_tipo='BackupDatabase',
                objeto_id=str(backup.id)
            )

            messages.success(request, f'Backup "{nombre}" creado exitosamente. Tamaño: {backup.tamaño_mb} MB')
            return redirect('sistema:gestionar_backups')

        except Exception as e:
            messages.error(request, f'Error al crear backup: {str(e)}')
            if 'backup' in locals():
                backup.estado = 'error'
                backup.save()
            return redirect('sistema:gestionar_backups')

    return render(request, 'sistema/crear_backup.html')

@login_required
def restaurar_backup(request, backup_id):
    """Restaurar la base de datos desde un backup"""
    backup = get_object_or_404(BackupDatabase, id=backup_id)

    if request.method == 'POST':
        if not backup.puede_restaurar:
            messages.error(request, 'Este backup no puede ser restaurado.')
            return redirect('sistema:gestionar_backups')

        # Obtener el usuario actual desde el modelo Usuario
        try:
            usuario_actual = Usuario.objects.get(numero_documento=request.user.username)
        except Usuario.DoesNotExist:
            usuario_actual = None

        try:
            # Crear un backup de seguridad antes de restaurar
            db_path = settings.DATABASES['default']['NAME']
            pre_restore_backup = f"{db_path}.pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
            shutil.copy2(db_path, pre_restore_backup)

            # Actualizar estado del backup
            backup.estado = 'restaurando'
            backup.save()

            # Restaurar el backup
            if os.path.exists(backup.ruta_archivo):
                # Cerrar todas las conexiones
                connection.close()

                # Copiar el backup sobre la base de datos actual
                shutil.copy2(backup.ruta_archivo, db_path)

                # Reconectar
                connection.connect()

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
                    descripcion=f'Base de datos restaurada desde: {backup.nombre}',
                    objeto_tipo='BackupDatabase',
                    objeto_id=str(backup.id)
                )

                messages.success(request, f'Base de datos restaurada exitosamente desde "{backup.nombre}". Se creó un backup de seguridad en: {pre_restore_backup}')
                return redirect('sistema:gestionar_backups')
            else:
                messages.error(request, 'El archivo de backup no existe.')
                backup.estado = 'error'
                backup.save()
                return redirect('sistema:gestionar_backups')

        except Exception as e:
            messages.error(request, f'Error al restaurar backup: {str(e)}')
            backup.estado = 'error'
            backup.save()

            # Intentar restaurar el backup de seguridad si existe
            if os.path.exists(pre_restore_backup):
                try:
                    connection.close()
                    shutil.copy2(pre_restore_backup, db_path)
                    connection.connect()
                    messages.warning(request, 'Se restauró la base de datos al estado anterior.')
                except:
                    pass

            return redirect('sistema:gestionar_backups')

    context = {
        'backup': backup
    }
    return render(request, 'sistema/confirmar_restaurar.html', context)

@login_required
def descargar_backup(request, backup_id):
    """Descargar un archivo de backup"""
    backup = get_object_or_404(BackupDatabase, id=backup_id)

    # Obtener el usuario actual desde el modelo Usuario
    try:
        usuario_actual = Usuario.objects.get(numero_documento=request.user.username)
    except Usuario.DoesNotExist:
        usuario_actual = None

    if backup.estado == 'completado' and os.path.exists(backup.ruta_archivo):
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

            response = FileResponse(open(backup.ruta_archivo, 'rb'), content_type='application/x-sqlite3')
            response['Content-Disposition'] = f'attachment; filename="{backup.nombre}.db"'
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

    # Obtener el usuario actual desde el modelo Usuario
    try:
        usuario_actual = Usuario.objects.get(numero_documento=request.user.username)
    except Usuario.DoesNotExist:
        usuario_actual = None

    if request.method == 'POST':
        nombre = backup.nombre
        ruta = backup.ruta_archivo

        # Debug: mostrar información
        messages.info(request, f'DEBUG: Iniciando eliminación de {nombre}')
        messages.info(request, f'DEBUG: Ruta del archivo: {ruta}')
        messages.info(request, f'DEBUG: ID del backup: {backup.id}')

        try:
            # Eliminar el archivo físico primero
            archivo_eliminado = False
            if ruta:
                if os.path.exists(ruta):
                    try:
                        os.remove(ruta)
                        archivo_eliminado = True
                        messages.info(request, f'DEBUG: Archivo físico eliminado')
                    except Exception as e:
                        messages.warning(request, f'No se pudo eliminar el archivo físico: {str(e)}')
                else:
                    messages.warning(request, f'DEBUG: Archivo no existe en: {ruta}')
            else:
                messages.warning(request, f'DEBUG: No hay ruta de archivo')

            # Registrar en log antes de eliminar el registro
            try:
                LogActividad.objects.create(
                    usuario=usuario_actual,
                    modulo='backups',
                    nivel='warning',
                    accion='eliminar_backup',
                    descripcion=f'Backup eliminado: {nombre}',
                    objeto_tipo='BackupDatabase',
                    objeto_id=str(backup.id)
                )
                messages.info(request, f'DEBUG: Log creado')
            except Exception as e:
                messages.warning(request, f'DEBUG: Error al crear log: {str(e)}')

            # Eliminar el registro de la base de datos
            try:
                backup_id_temp = str(backup.id)
                backup.delete()
                messages.success(request, f'✓ Backup "{nombre}" (ID: {backup_id_temp}) eliminado exitosamente.')
                messages.info(request, f'DEBUG: Registro eliminado de la BD')
            except Exception as e:
                messages.error(request, f'ERROR al eliminar registro de BD: {str(e)}')
                raise

        except Exception as e:
            messages.error(request, f'Error general al eliminar backup: {str(e)}')

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
    """Crear backup rápido con un click (AJAX)"""
    if request.method == 'POST':
        try:
            import json

            # Obtener el usuario actual desde el modelo Usuario
            try:
                usuario_actual = Usuario.objects.get(numero_documento=request.user.username)
            except Usuario.DoesNotExist:
                usuario_actual = None

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
                version_django=settings.VERSION if hasattr(settings, 'VERSION') else '5.2.7',
                version_python=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            )

            # Ruta de la base de datos actual
            db_path = settings.DATABASES['default']['NAME']

            # Crear directorio de backups si no existe
            backup_dir = os.path.join(settings.MEDIA_ROOT, 'backups', datetime.now().strftime('%Y'), datetime.now().strftime('%m'))
            os.makedirs(backup_dir, exist_ok=True)

            # Nombre del archivo de backup
            backup_filename = f'backup_{backup.id}.db'
            backup_path = os.path.join(backup_dir, backup_filename)

            # Copiar la base de datos
            shutil.copy2(db_path, backup_path)

            # Obtener tamaño del archivo
            tamaño = os.path.getsize(backup_path)

            # Contar tablas y registros
            total_registros = 0
            total_tablas = 0
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                    tablas = cursor.fetchall()
                    total_tablas = len(tablas)

                    for tabla in tablas:
                        cursor.execute(f"SELECT COUNT(*) FROM {tabla[0]}")
                        count = cursor.fetchone()[0]
                        total_registros += count
            except Exception as e:
                print(f"Error contando: {e}")

            # Actualizar el backup
            backup.ruta_archivo = backup_path
            backup.tamaño_bytes = tamaño
            backup.total_tablas = total_tablas
            backup.total_registros = total_registros
            backup.estado = 'completado'
            backup.fecha_completado = timezone.now()
            backup.save()

            # Registrar en log
            LogActividad.objects.create(
                usuario=usuario_actual,
                modulo='backups',
                nivel='info',
                accion='crear_backup_rapido',
                descripcion=f'Backup rápido creado: {nombre}',
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
            return JsonResponse({
                'success': False,
                'message': f'Error al crear backup: {str(e)}'
            }, status=500)

    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)
