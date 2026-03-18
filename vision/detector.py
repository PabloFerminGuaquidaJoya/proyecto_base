"""
Módulo de detección visual para maquinaria pesada y componentes.
Usa TFLite si el modelo está disponible, de lo contrario informa al usuario.
"""
import logging
import os

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mapeos de clases detectables
# ---------------------------------------------------------------------------

# Máquinas completas → CategoriaMaquina (nombre exacto del seed)
CLASE_A_CATEGORIA = {
    'excavadora':       'Maquinaria de Excavación y Movimiento de Tierras',
    'bulldozer':        'Maquinaria de Excavación y Movimiento de Tierras',
    'retroexcavadora':  'Maquinaria de Excavación y Movimiento de Tierras',
    'grua_torre':       'Maquinaria de Elevación y Izaje',
    'grua_movil':       'Maquinaria de Elevación y Izaje',
    'compactadora':     'Maquinaria de Nivelación y Compactación',
    'cargador_frontal': 'Maquinaria de Carga y Transporte',
    'camion_minero':    'Maquinaria de Carga y Transporte',
    'perforadora':      'Maquinaria de Perforación',
    'motoniveladora':   'Maquinaria de Nivelación y Compactación',
    'pavimentadora':    'Maquinaria de Nivelación y Compactación',
    'volquete':         'Maquinaria de Carga y Transporte',
}

# Componentes/piezas (para inventario)
COMPONENTES = [
    'cucharon', 'orugas', 'brazo_hidraulico', 'cabina_operador',
    'hoja_topadora', 'contrapeso', 'pluma_grua', 'neumatico_pesado',
    'cilindro_hidraulico', 'motor_diesel', 'tren_de_rodaje',
    'gancho_grua', 'cucharona_cargador',
]

# Nombres legibles para mostrar en la UI
NOMBRES_DISPLAY = {
    'excavadora':          'Excavadora',
    'bulldozer':           'Bulldozer / Topadora',
    'retroexcavadora':     'Retroexcavadora',
    'grua_torre':          'Grúa Torre',
    'grua_movil':          'Grúa Móvil',
    'compactadora':        'Compactadora / Rodillo Vibratorio',
    'cargador_frontal':    'Cargador Frontal',
    'camion_minero':       'Camión Minero',
    'perforadora':         'Perforadora',
    'motoniveladora':      'Motoniveladora',
    'pavimentadora':       'Pavimentadora',
    'volquete':            'Volquete / Camión Volco',
    'cucharon':            'Cucharon / Balde',
    'orugas':              'Orugas / Cadenas',
    'brazo_hidraulico':    'Brazo Hidráulico',
    'cabina_operador':     'Cabina Operador',
    'hoja_topadora':       'Hoja Topadora',
    'contrapeso':          'Contrapeso',
    'pluma_grua':          'Pluma de Grúa',
    'neumatico_pesado':    'Neumático Pesado',
    'cilindro_hidraulico': 'Cilindro Hidráulico',
    'motor_diesel':        'Motor Diésel',
    'tren_de_rodaje':      'Tren de Rodaje',
    'gancho_grua':         'Gancho de Grúa',
    'cucharona_cargador':  'Cucharona de Cargador',
}

LABELS = list(CLASE_A_CATEGORIA.keys()) + COMPONENTES

# ---------------------------------------------------------------------------
# Estado global del módulo
# ---------------------------------------------------------------------------
_interpreter = None
_modelo_disponible = False
_umbral = 0.5


def inicializar():
    """Llamado desde apps.py → ready(). Intenta cargar el modelo TFLite."""
    global _interpreter, _modelo_disponible, _umbral

    try:
        from django.conf import settings
        model_path = str(getattr(settings, 'VISION_MODEL_PATH', ''))
        _umbral = float(getattr(settings, 'VISION_CONFIDENCE_THRESHOLD', 0.5))

        if not model_path:
            logger.info("Vision: VISION_MODEL_PATH no configurado. Detección IA desactivada.")
            return

        if not os.path.exists(model_path):
            logger.info(
                f"Vision: Modelo no encontrado en '{model_path}'. "
                "Descarga o entrena el modelo para activar la detección IA."
            )
            return

        # Intentar con tflite_runtime primero, luego tensorflow
        try:
            import tflite_runtime.interpreter as tflite
            _interpreter = tflite.Interpreter(model_path=model_path)
            logger.info("Vision: Usando tflite_runtime.")
        except ImportError:
            import tensorflow as tf
            _interpreter = tf.lite.Interpreter(model_path=model_path)
            logger.info("Vision: Usando tensorflow.lite.")

        _interpreter.allocate_tensors()
        _modelo_disponible = True
        logger.info("Vision: Modelo TFLite cargado correctamente.")

    except Exception as e:
        logger.error(f"Vision: Error al inicializar modelo: {e}")


# ---------------------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------------------

def detectar(imagen_bytes: bytes) -> dict:
    """
    Detecta maquinaria pesada o componente en la imagen.

    Retorna dict con:
        modelo_disponible (bool)
        detectado         (bool)
        clase             (str)  — clave interna ej. 'excavadora'
        clase_display     (str)  — nombre legible ej. 'Excavadora'
        confianza         (float 0-1)
        categoria_maquina (str|None) — nombre de CategoriaMaquina para FK
        es_componente     (bool)
        top3              (list)
        mensaje           (str)
    """
    if not _modelo_disponible:
        return {
            'modelo_disponible': False,
            'mensaje': (
                'Modelo de IA no disponible. '
                'Coloca el archivo heavy_machinery.tflite en vision/models/ '
                'y configura VISION_MODEL_PATH en settings.py para activar esta función.'
            ),
        }

    try:
        img = _decodificar(imagen_bytes)
        if img is None:
            return {
                'modelo_disponible': True,
                'detectado': False,
                'mensaje': 'No se pudo leer la imagen. Asegúrate de subir un JPG o PNG.',
            }

        processed = _preprocesar(img)

        input_details  = _interpreter.get_input_details()
        output_details = _interpreter.get_output_details()
        _interpreter.set_tensor(input_details[0]['index'], processed)
        _interpreter.invoke()
        predictions = _interpreter.get_tensor(output_details[0]['index'])[0]

        top_indices = np.argsort(predictions)[-3:][::-1]
        max_idx  = int(top_indices[0])
        max_conf = float(predictions[max_idx])

        if max_conf < _umbral:
            return {
                'modelo_disponible': True,
                'detectado': False,
                'confianza': round(max_conf, 3),
                'mensaje': (
                    f'No se detectó ninguna maquinaria con suficiente confianza '
                    f'(máx: {max_conf:.0%}). Intenta con una foto más clara.'
                ),
            }

        clase        = LABELS[max_idx] if max_idx < len(LABELS) else 'desconocido'
        categoria    = CLASE_A_CATEGORIA.get(clase)
        es_componente = clase not in CLASE_A_CATEGORIA

        top3 = [
            {
                'clase':         LABELS[i],
                'clase_display': NOMBRES_DISPLAY.get(LABELS[i], LABELS[i]),
                'confianza':     round(float(predictions[i]), 3),
            }
            for i in top_indices
            if i < len(LABELS) and predictions[i] > 0.05
        ]

        return {
            'modelo_disponible': True,
            'detectado':         True,
            'clase':             clase,
            'clase_display':     NOMBRES_DISPLAY.get(clase, clase),
            'confianza':         round(max_conf, 3),
            'categoria_maquina': categoria,
            'es_componente':     es_componente,
            'top3':              top3,
            'mensaje':           f'Detectado: {NOMBRES_DISPLAY.get(clase, clase)} ({max_conf:.0%} confianza)',
        }

    except Exception as e:
        logger.error(f"Vision: Error en detección: {e}")
        return {
            'modelo_disponible': True,
            'detectado': False,
            'mensaje': f'Error procesando la imagen: {e}',
        }


# ---------------------------------------------------------------------------
# Utilidades internas
# ---------------------------------------------------------------------------

def _decodificar(imagen_bytes: bytes):
    arr = np.frombuffer(imagen_bytes, dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


def _preprocesar(img):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_r   = cv2.resize(img_rgb, (224, 224))
    img_n   = img_r.astype(np.float32) / 255.0
    return np.expand_dims(img_n, axis=0)


def estado() -> dict:
    """Para el endpoint de estado del sistema."""
    return {
        'modelo_disponible': _modelo_disponible,
        'umbral':            _umbral,
        'total_clases':      len(LABELS),
        'clases_maquinaria': list(CLASE_A_CATEGORIA.keys()),
        'clases_componentes': COMPONENTES,
    }
