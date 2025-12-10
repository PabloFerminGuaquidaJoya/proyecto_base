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
    centro_formacion = models.CharField(max_length=200)
    especialidad = models.CharField(max_length=200, blank=True)
    cargo = models.CharField(max_length=100, blank=True)

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

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.numero_documento})"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

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
