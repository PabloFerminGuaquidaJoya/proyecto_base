"""
Módulo de reconocimiento facial usando DeepFace.
Extrae embeddings faciales sin almacenar imágenes.
"""

import base64
from typing import Tuple, Optional, Dict, List
import logging
import os

logger = logging.getLogger(__name__)

# Suprimir warnings de TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Importaciones lazy - se cargan cuando se necesitan
deepface = None
np = None
cv2 = None


def _load_dependencies():
    """Carga las dependencias de forma lazy"""
    global deepface, np, cv2
    if deepface is None:
        try:
            # Suprimir warnings
            import warnings
            warnings.filterwarnings('ignore')

            from deepface import DeepFace as _df
            import numpy as _np
            import cv2 as _cv2
            deepface = _df
            np = _np
            cv2 = _cv2
            return True
        except ImportError as e:
            logger.error(f"Error importando dependencias de reconocimiento facial: {e}")
            return False
    return True


class FacialRecognitionService:
    """
    Servicio para detección facial y extracción de embeddings.
    Utiliza DeepFace para procesamiento preciso.
    """

    # Configuración
    MODEL_NAME = "Facenet"  # Opciones: VGG-Face, Facenet, Facenet512, OpenFace, DeepFace, ArcFace
    DETECTOR_BACKEND = "opencv"  # Opciones: opencv, ssd, mtcnn, retinaface, mediapipe
    THRESHOLD_SIMILITUD = 0.6  # Similitud mínima para autenticación (60%)
    DISTANCE_METRIC = "cosine"  # Opciones: cosine, euclidean, euclidean_l2

    def __init__(self):
        """Inicializa el servicio (lazy)"""
        self._initialized = False

    def _ensure_initialized(self) -> bool:
        """Asegura que el servicio esté inicializado"""
        if self._initialized:
            return True

        if not _load_dependencies():
            return False

        self._initialized = True
        return True

    def is_available(self) -> bool:
        """Verifica si el servicio está disponible"""
        return self._ensure_initialized()

    def decode_base64_image(self, base64_string: str):
        """
        Decodifica una imagen en base64 a formato numpy array.

        Args:
            base64_string: Imagen codificada en base64

        Returns:
            np.ndarray: Imagen en formato BGR
        """
        if not self._ensure_initialized():
            return None

        try:
            # Remover prefijo de data URL si existe
            if 'base64,' in base64_string:
                base64_string = base64_string.split('base64,')[1]

            # Decodificar
            img_data = base64.b64decode(base64_string)
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            return img
        except Exception as e:
            logger.error(f"Error decodificando imagen base64: {str(e)}")
            return None

    def detectar_rostro(self, imagen) -> Tuple[bool, Optional[Dict], str]:
        """
        Detecta si hay exactamente un rostro en la imagen.

        Args:
            imagen: Imagen en formato numpy array (BGR)

        Returns:
            Tuple[bool, Optional[Dict], str]:
                - bool: True si se detectó exactamente un rostro
                - Dict: Información del rostro detectado
                - str: Mensaje de error o éxito
        """
        if not self._ensure_initialized():
            return False, None, "Servicio de reconocimiento facial no disponible"

        try:
            # Detectar rostros usando DeepFace
            faces = deepface.extract_faces(
                img_path=imagen,
                detector_backend=self.DETECTOR_BACKEND,
                enforce_detection=False
            )

            # Filtrar rostros con baja confianza
            valid_faces = [f for f in faces if f.get('confidence', 0) > 0.5]

            if len(valid_faces) == 0:
                return False, None, "No se detectó ningún rostro en la imagen"

            if len(valid_faces) > 1:
                return False, None, "Se detectaron múltiples rostros. Por favor, capture solo un rostro"

            # Exactamente un rostro detectado
            face = valid_faces[0]
            facial_area = face.get('facial_area', {})

            rostro_info = {
                'bbox': facial_area,
                'confianza': face.get('confidence', 1.0)
            }

            return True, rostro_info, "Rostro detectado correctamente"

        except Exception as e:
            logger.error(f"Error en detección de rostro: {str(e)}")
            # Si hay error de detección, intentar extraer embedding directamente
            return False, None, f"Error en detección de rostro: {str(e)}"

    def extraer_embedding(self, imagen) -> Tuple[bool, Optional[List[float]], str]:
        """
        Extrae el embedding facial (vector de características) de la imagen.

        Args:
            imagen: Imagen en formato numpy array (BGR)

        Returns:
            Tuple[bool, Optional[List[float]], str]:
                - bool: True si se extrajo correctamente
                - List[float]: Vector de embedding
                - str: Mensaje de error o éxito
        """
        if not self._ensure_initialized():
            return False, None, "Servicio de reconocimiento facial no disponible"

        try:
            # Extraer embedding usando DeepFace
            embedding_objs = deepface.represent(
                img_path=imagen,
                model_name=self.MODEL_NAME,
                detector_backend=self.DETECTOR_BACKEND,
                enforce_detection=False
            )

            if not embedding_objs or len(embedding_objs) == 0:
                return False, None, "No se pudo extraer el embedding facial"

            if len(embedding_objs) > 1:
                return False, None, "Se detectaron múltiples rostros. Por favor, capture solo un rostro"

            # Obtener el embedding (lista de floats)
            embedding = embedding_objs[0].get('embedding', [])

            if not embedding:
                return False, None, "Error extrayendo características faciales"

            return True, embedding, "Embedding extraído correctamente"

        except ValueError as e:
            error_msg = str(e)
            if "Face could not be detected" in error_msg:
                return False, None, "No se detectó ningún rostro en la imagen. Asegúrese de estar frente a la cámara."
            return False, None, f"Error: {error_msg}"
        except Exception as e:
            logger.error(f"Error extrayendo embedding: {str(e)}")
            return False, None, f"Error técnico: {str(e)}"

    def calcular_similitud(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calcula la similitud entre dos embeddings usando similitud coseno.

        Args:
            embedding1: Primer vector de características
            embedding2: Segundo vector de características

        Returns:
            float: Similitud entre 0 y 1 (1 = idénticos)
        """
        if not self._ensure_initialized():
            return 0.0

        try:
            # Convertir a numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            # Similitud coseno
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similitud = dot_product / (norm1 * norm2)

            # Normalizar a rango [0, 1] (coseno va de -1 a 1)
            similitud = (similitud + 1) / 2

            return float(similitud)

        except Exception as e:
            logger.error(f"Error calculando similitud: {str(e)}")
            return 0.0

    def verificar_autenticacion(self, embedding_capturado: List[float],
                                embedding_almacenado: List[float]) -> Tuple[bool, float, str]:
        """
        Verifica si un embedding capturado coincide con el almacenado.

        Args:
            embedding_capturado: Embedding del rostro capturado
            embedding_almacenado: Embedding almacenado en la base de datos

        Returns:
            Tuple[bool, float, str]:
                - bool: True si la autenticación es exitosa
                - float: Nivel de similitud
                - str: Mensaje explicativo
        """
        similitud = self.calcular_similitud(embedding_capturado, embedding_almacenado)

        if similitud >= self.THRESHOLD_SIMILITUD:
            return True, similitud, f"Autenticación exitosa (similitud: {similitud:.2%})"
        else:
            return False, similitud, f"Rostro no coincide (similitud: {similitud:.2%})"

    def validar_calidad_imagen(self, imagen) -> Tuple[bool, str]:
        """
        Valida que la imagen tenga calidad suficiente para reconocimiento.

        Verifica:
        - Resolución mínima
        - No esté muy oscura/clara
        """
        if not self._ensure_initialized():
            return False, "Servicio de reconocimiento facial no disponible"

        try:
            height, width = imagen.shape[:2]

            # Verificar resolución mínima (320x240)
            if width < 320 or height < 240:
                return False, "Resolución de imagen muy baja. Mínimo 320x240 píxeles"

            # Verificar brillo promedio
            gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
            brillo = np.mean(gray)

            if brillo < 40:
                return False, "Imagen muy oscura. Mejore la iluminación"
            if brillo > 220:
                return False, "Imagen muy clara. Reduzca la iluminación"

            return True, "Calidad de imagen adecuada"

        except Exception as e:
            logger.error(f"Error validando calidad: {str(e)}")
            return False, f"Error validando calidad: {str(e)}"


# Instancia global del servicio (se inicializa lazy)
facial_service = FacialRecognitionService()
