# -*- coding: utf-8 -*-
"""
Signals que disparan backups automáticos al crear registros clave.
Se ejecutan en un hilo separado para no bloquear la respuesta HTTP.
"""
import threading
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

# Tiempo mínimo entre backups por evento (segundos) para evitar ráfagas
_MIN_INTERVALO_SEGUNDOS = 300  # 5 minutos
_ultimo_backup_evento = {}
_lock = threading.Lock()


def _puede_hacer_backup(trigger_key):
    """Retorna True si han pasado al menos _MIN_INTERVALO_SEGUNDOS desde el último backup del mismo tipo."""
    import time
    with _lock:
        ultimo = _ultimo_backup_evento.get(trigger_key, 0)
        ahora = time.time()
        if ahora - ultimo >= _MIN_INTERVALO_SEGUNDOS:
            _ultimo_backup_evento[trigger_key] = ahora
            return True
        return False


def _lanzar_backup_en_hilo(tipo, descripcion, trigger_key):
    """Lanza el backup en un daemon thread para no bloquear la petición."""
    if not _puede_hacer_backup(trigger_key):
        logger.debug(f"Backup '{trigger_key}' omitido por intervalo mínimo.")
        return

    def _run():
        from sistema.backup_service import crear_backup_automatico
        crear_backup_automatico(tipo=tipo, descripcion=descripcion)

    t = threading.Thread(target=_run, daemon=True)
    t.start()


# ── Documento ────────────────────────────────────────────────────────────────

def _signal_documento(sender, instance, created, **kwargs):
    if created:
        _lanzar_backup_en_hilo(
            tipo='automatico',
            descripcion='Backup automático — nuevo documento subido',
            trigger_key='documento',
        )


# ── Máquina ──────────────────────────────────────────────────────────────────

def _signal_maquina(sender, instance, created, **kwargs):
    if created:
        _lanzar_backup_en_hilo(
            tipo='automatico',
            descripcion='Backup automático — nueva máquina registrada',
            trigger_key='maquina',
        )


# ── Pieza de Inventario ───────────────────────────────────────────────────────

def _signal_pieza(sender, instance, created, **kwargs):
    if created:
        _lanzar_backup_en_hilo(
            tipo='automatico',
            descripcion='Backup automático — nueva pieza de inventario registrada',
            trigger_key='pieza_inventario',
        )


def conectar_signals():
    """
    Conecta todos los signals. Se llama desde AppConfig.ready() de cada app.
    Usar lazy imports para evitar problemas de inicialización.
    """
    try:
        from documentos.models import Documento
        post_save.connect(_signal_documento, sender=Documento, weak=False)
        logger.debug("Signal backup conectado: Documento")
    except Exception as e:
        logger.warning(f"No se pudo conectar signal Documento: {e}")

    try:
        from maquinaria.models import Maquina
        post_save.connect(_signal_maquina, sender=Maquina, weak=False)
        logger.debug("Signal backup conectado: Maquina")
    except Exception as e:
        logger.warning(f"No se pudo conectar signal Maquina: {e}")

    try:
        from inventario.models import PiezaInventario
        post_save.connect(_signal_pieza, sender=PiezaInventario, weak=False)
        logger.debug("Signal backup conectado: PiezaInventario")
    except Exception as e:
        logger.warning(f"No se pudo conectar signal PiezaInventario: {e}")
