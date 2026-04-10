import logging
import os

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class SistemaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sistema'
    verbose_name = 'Sistema'

    def ready(self):
        # Conectar signals de backup
        from sistema.signals import conectar_signals
        conectar_signals()

        # Iniciar scheduler solo en el proceso hijo de auto-reload (desarrollo)
        # o en producción donde RUN_MAIN no está definido.
        # Esto evita que el scheduler corra dos veces con runserver --reload.
        run_main = os.environ.get('RUN_MAIN')
        if run_main == 'true' or run_main is None:
            self._iniciar_scheduler()

    def _iniciar_scheduler(self):
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.interval import IntervalTrigger

            scheduler = BackgroundScheduler(timezone='America/Bogota')
            scheduler.add_job(
                func=_job_backup_periodico,
                trigger=IntervalTrigger(hours=2),
                id='backup_automatico_2h',
                replace_existing=True,
                misfire_grace_time=600,
            )
            scheduler.start()
            logger.info("Scheduler de backups automáticos iniciado (cada 2 horas).")
        except ImportError:
            logger.warning(
                "apscheduler no está instalado. "
                "Ejecuta: pip install apscheduler"
            )
        except Exception as e:
            logger.error(f"Error iniciando scheduler de backups: {e}", exc_info=True)


def _job_backup_periodico():
    """Tarea ejecutada por APScheduler cada 2 horas."""
    from django.db import close_old_connections
    close_old_connections()
    from sistema.backup_service import crear_backup_automatico
    crear_backup_automatico(
        tipo='programado',
        descripcion='Backup automático programado — cada 2 horas',
    )
