from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class TipoUsuario(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    permisos = models.JSONField(default=dict)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tipo de Usuario"
        verbose_name_plural = "Tipos de Usuario"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Usuario(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('TI', 'Tarjeta de Identidad'),
        ('CE', 'Cédula de Extranjería'),
        ('PAS', 'Pasaporte'),
    ]

    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('suspendido', 'Suspendido'),
        ('pendiente', 'Pendiente Aprobación'),
    ]

    # Información personal
    tipo_documento = models.CharField(max_length=3, choices=TIPO_DOCUMENTO_CHOICES, default='CC')
    numero_documento = models.CharField(
        max_length=20,
        unique=True,
        validators=[RegexValidator(regex=r'^\d+$', message='Solo se permiten números')]
    )
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    foto_perfil = models.ImageField(upload_to='usuarios/fotos/', blank=True, null=True)

    # Información institucional
    tipo_usuario = models.ForeignKey(TipoUsuario, on_delete=models.PROTECT)
    centro_formacion = models.ForeignKey(
        'sistema.CentroFormacion',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='Centro de Formación'
    )
    especialidad = models.CharField(max_length=200, blank=True)
    cargo = models.CharField(max_length=100, blank=True)
    ficha = models.ForeignKey(
        'sistema.Ficha',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='Ficha'
    )

    # Estado y fechas
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)

    # Configuraciones
    notificaciones_email = models.BooleanField(default=True)
    tema_oscuro = models.BooleanField(default=False)
    idioma = models.CharField(max_length=10, default='es')

    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios_creados')

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['numero_documento']),
            models.Index(fields=['email']),
            models.Index(fields=['estado']),
        ]

    @staticmethod
    def _capitalizar_nombre(valor):
        """Capitaliza la primera letra de cada palabra del nombre/apellido."""
        if not valor:
            return valor
        return ' '.join(palabra.capitalize() for palabra in valor.strip().split())

    def save(self, *args, **kwargs):
        self.nombres   = self._capitalizar_nombre(self.nombres)
        self.apellidos = self._capitalizar_nombre(self.apellidos)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.numero_documento})"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    @property
    def primer_nombre(self):
        return self.nombres.split()[0] if self.nombres else ''

    @property
    def iniciales(self):
        n = self.nombres[0].upper() if self.nombres else 'U'
        a = self.apellidos[0].upper() if self.apellidos else 'S'
        return f"{n}{a}"

    @property
    def esta_activo(self):
        return self.estado == 'activo'

class SesionUsuario(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='sesiones')
    token_sesion = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Sesión de Usuario"
        verbose_name_plural = "Sesiones de Usuario"
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"Sesión de {self.usuario.nombre_completo} - {self.fecha_inicio}"

class TokenRecuperacionPassword(models.Model):
    """Modelo para almacenar tokens de recuperación de contraseña"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='tokens_recuperacion')
    token = models.CharField(max_length=100, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()
    usado = models.BooleanField(default=False)
    ip_solicitud = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = "Token de Recuperación"
        verbose_name_plural = "Tokens de Recuperación"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Token de {self.usuario.email} - {self.fecha_creacion}"

    def esta_expirado(self):
        """Verifica si el token ha expirado"""
        from django.utils import timezone
        return timezone.now() > self.fecha_expiracion

    def es_valido(self):
        """Verifica si el token es válido (no usado y no expirado)"""
        return not self.usado and not self.esta_expirado()


class ReconocimientoFacial(models.Model):
    """
    Modelo para almacenar embeddings faciales de usuarios.
    No almacena imágenes, solo vectores numéricos para privacidad.
    """
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='reconocimiento_facial'
    )

    # Embedding facial (vector de 128 dimensiones de MediaPipe)
    embedding = models.JSONField(
        help_text='Vector de características faciales (128 dimensiones)'
    )

    # Metadatos
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(
        default=True,
        help_text='Indica si el reconocimiento facial está activo para este usuario'
    )

    # Datos de calidad
    confianza_registro = models.FloatField(
        help_text='Nivel de confianza de la detección facial durante el registro (0-1)'
    )

    # Auditoría
    ip_registro = models.GenericIPAddressField(null=True, blank=True)
    user_agent_registro = models.TextField(blank=True)

    class Meta:
        verbose_name = "Reconocimiento Facial"
        verbose_name_plural = "Reconocimientos Faciales"
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"Reconocimiento facial de {self.usuario.nombre_completo}"


class IntentoReconocimientoFacial(models.Model):
    """
    Modelo para registrar todos los intentos de autenticación facial.
    Importante para seguridad y detección de intentos de acceso no autorizado.
    """
    TIPO_INTENTO_CHOICES = [
        ('registro', 'Registro de rostro'),
        ('login', 'Inicio de sesión'),
        ('actualizacion', 'Actualización de rostro'),
    ]

    RESULTADO_CHOICES = [
        ('exitoso', 'Exitoso'),
        ('fallido', 'Fallido'),
        ('error', 'Error técnico'),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='intentos_reconocimiento',
        null=True,
        blank=True
    )
    tipo_intento = models.CharField(max_length=20, choices=TIPO_INTENTO_CHOICES)
    resultado = models.CharField(max_length=20, choices=RESULTADO_CHOICES)

    # Detalles del intento
    similitud = models.FloatField(
        null=True,
        blank=True,
        help_text='Nivel de similitud calculado (0-1)'
    )
    mensaje_error = models.TextField(blank=True)

    # Auditoría
    fecha_intento = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()

    class Meta:
        verbose_name = "Intento de Reconocimiento Facial"
        verbose_name_plural = "Intentos de Reconocimiento Facial"
        ordering = ['-fecha_intento']
        indexes = [
            models.Index(fields=['usuario', '-fecha_intento']),
            models.Index(fields=['resultado', '-fecha_intento']),
        ]

    def __str__(self):
        usuario_str = self.usuario.nombre_completo if self.usuario else "Desconocido"
        return f"{self.get_tipo_intento_display()} - {usuario_str} - {self.resultado}"
