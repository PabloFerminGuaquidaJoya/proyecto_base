# -*- coding: utf-8 -*-
"""
Servicio de backup automático.
Puede ser invocado desde signals, scheduler o vistas.
"""
import os
import sys
import logging
from datetime import datetime

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def crear_backup_automatico(tipo='automatico', descripcion=''):
    """
    Crea un backup de la base de datos sin requerir un request HTTP.
    Se usa desde el scheduler cada 2 horas y desde los signals post_save.
    Retorna True si tuvo éxito, False si falló.
    """
    from django.db import close_old_connections
    close_old_connections()

    try:
        from sistema.models import BackupDatabase, LogActividad
        from sistema.views import _ejecutar_mysqldump, _contar_tablas_y_registros

        nombre = f'Auto_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        desc = descripcion or f'Backup automático — {tipo}'

        backup = BackupDatabase.objects.create(
            nombre=nombre,
            descripcion=desc,
            tipo=tipo,
            estado='creando',
            version_django=getattr(settings, 'VERSION', '5.2'),
            version_python=(
                f"{sys.version_info.major}."
                f"{sys.version_info.minor}."
                f"{sys.version_info.micro}"
            ),
        )

        backup_dir = os.path.join(
            settings.MEDIA_ROOT, 'backups',
            datetime.now().strftime('%Y'),
            datetime.now().strftime('%m'),
        )
        os.makedirs(backup_dir, exist_ok=True)

        backup_path = os.path.abspath(os.path.join(backup_dir, f'backup_{backup.id}.sql'))
        exito, mensaje = _ejecutar_mysqldump(backup_path)

        if not exito:
            backup.estado = 'error'
            backup.metadatos = {'error': mensaje}
            backup.save()
            logger.error(f"Backup automático fallido: {mensaje}")
            return False

        tamaño = os.path.getsize(backup_path) if os.path.exists(backup_path) else 0
        total_tablas, total_registros = _contar_tablas_y_registros()

        backup.ruta_archivo = backup_path
        backup.tamaño_bytes = tamaño
        backup.total_tablas = total_tablas
        backup.total_registros = total_registros
        backup.estado = 'completado'
        backup.fecha_completado = timezone.now()
        backup.metadatos = {
            'engine': 'MySQL',
            'database': settings.DATABASES['default']['NAME'],
            'trigger': tipo,
        }
        backup.save()

        LogActividad.objects.create(
            modulo='backups',
            nivel='info',
            accion='backup_automatico',
            descripcion=f'Backup automático creado: {nombre} ({tipo})',
            objeto_tipo='BackupDatabase',
            objeto_id=str(backup.id),
        )

        logger.info(f"Backup automático creado exitosamente: {nombre} ({tamaño} bytes)")
        return True

    except Exception as e:
        logger.error(f"Error inesperado en backup automático: {e}", exc_info=True)
        return False
