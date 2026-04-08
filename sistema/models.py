# -*- coding: utf-8 -*-
from django.db import models
import uuid

class Configuracion(models.Model):
    TIPO_VALOR_CHOICES = [
        ('string', 'Texto'),
        ('integer', 'Numero Entero'),
        ('float', 'Numero Decimal'),
        ('boolean', 'Verdadero/Falso'),
        ('json', 'JSON'),
        ('date', 'Fecha'),
        ('datetime', 'Fecha y Hora'),
        ('email', 'Correo Electronico'),
        ('url', 'URL'),
    ]

    clave = models.CharField(max_length=100, unique=True)
    valor = models.TextField()
    tipo_valor = models.CharField(max_length=10, choices=TIPO_VALOR_CHOICES, default='string')
    descripcion = models.TextField(blank=True)
    categoria = models.CharField(max_length=50, default='general')

    # Control de acceso
    publico = models.BooleanField(default=False)
    modificable = models.BooleanField(default=True)

    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    modificado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        verbose_name = "Configuracion"
        verbose_name_plural = "Configuraciones"
        ordering = ['categoria', 'clave']

    def __str__(self):
        return f"{self.clave} = {self.valor[:50]}"

    def get_valor_typed(self):
        if self.tipo_valor == 'integer':
            return int(self.valor)
        elif self.tipo_valor == 'float':
            return float(self.valor)
        elif self.tipo_valor == 'boolean':
            return self.valor.lower() in ('true', '1', 'yes', 'on')
        elif self.tipo_valor == 'json':
            import json
            return json.loads(self.valor)
        return self.valor

class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('info', 'Informacion'),
        ('success', 'Exito'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
        ('system', 'Sistema'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('enviada', 'Enviada'),
        ('leida', 'Leida'),
        ('archivada', 'Archivada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        related_name='notificaciones'
    )

    # Contenido
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='info')
    icono = models.CharField(max_length=50, default='bi-bell')

    # Estado y fechas
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    fecha_archivado = models.DateTimeField(null=True, blank=True)

    # Configuracion
    requiere_accion = models.BooleanField(default=False)
    url_accion = models.URLField(blank=True)
    texto_accion = models.CharField(max_length=100, blank=True)

    # Relaciones opcionales
    maquina_relacionada = models.ForeignKey(
        'maquinaria.Maquina',
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    alerta_relacionada = models.ForeignKey(
        'maquinaria.AlertaMaquina',
        on_delete=models.CASCADE,
        null=True, blank=True
    )

    # Metadatos
    metadatos = models.JSONField(default=dict, blank=True)
    enviado_por_sistema = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Notificacion"
        verbose_name_plural = "Notificaciones"
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['usuario', 'estado']),
            models.Index(fields=['fecha_creacion']),
            models.Index(fields=['tipo']),
        ]

    def __str__(self):
        return f"{self.titulo} - {self.usuario.nombre_completo}"

class LogActividad(models.Model):
    NIVEL_CHOICES = [
        ('debug', 'Debug'),
        ('info', 'Informacion'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
        ('critical', 'Critico'),
    ]

    MODULO_CHOICES = [
        ('usuarios', 'Usuarios'),
        ('maquinaria', 'Maquinaria'),
        ('reportes', 'Reportes'),
        ('documentos', 'Documentos'),
        ('sistema', 'Sistema'),
        ('backups', 'Copias de Seguridad'),
        ('api', 'API'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Informacion basica
    timestamp = models.DateTimeField(auto_now_add=True)
    nivel = models.CharField(max_length=10, choices=NIVEL_CHOICES, default='info')
    modulo = models.CharField(max_length=20, choices=MODULO_CHOICES, default='sistema')

    # Usuario y sesion
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    sesion_id = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # Accion realizada
    accion = models.CharField(max_length=100)
    descripcion = models.TextField()
    objeto_tipo = models.CharField(max_length=50, blank=True)  # Modelo afectado
    objeto_id = models.CharField(max_length=100, blank=True)  # ID del objeto

    # Detalles tecnicos
    request_method = models.CharField(max_length=10, blank=True)  # GET, POST, etc.
    request_path = models.CharField(max_length=500, blank=True)
    user_agent = models.TextField(blank=True)

    # Metadatos adicionales
    datos_adicionales = models.JSONField(default=dict, blank=True)
    tiempo_ejecucion = models.DurationField(null=True, blank=True)

    class Meta:
        verbose_name = "Log de Actividad"
        verbose_name_plural = "Logs de Actividad"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['usuario', 'timestamp']),
            models.Index(fields=['modulo', 'timestamp']),
            models.Index(fields=['nivel']),
            models.Index(fields=['accion']),
        ]

    def __str__(self):
        usuario_str = self.usuario.nombre_completo if self.usuario else 'Sistema'
        return f"{self.timestamp} - {usuario_str} - {self.accion}"

class BackupDatabase(models.Model):
    """Modelo para gestionar copias de seguridad de la base de datos"""
    ESTADO_CHOICES = [
        ('creando', 'Creando'),
        ('completado', 'Completado'),
        ('error', 'Error'),
        ('restaurando', 'Restaurando'),
        ('restaurado', 'Restaurado'),
    ]

    TIPO_CHOICES = [
        ('manual', 'Manual'),
        ('automatico', 'Automático'),
        ('programado', 'Programado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Información básica
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, default='manual')

    # Archivo de backup
    archivo = models.FileField(upload_to='backups/%Y/%m/', null=True, blank=True)
    ruta_archivo = models.CharField(max_length=500, blank=True)
    tamaño_bytes = models.BigIntegerField(default=0)

    # Estado y fechas
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='creando')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)

    # Usuario responsable
    creado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='backups_creados'
    )

    # Estadísticas del backup
    total_tablas = models.IntegerField(default=0)
    total_registros = models.IntegerField(default=0)

    # Información de restauración
    fecha_restauracion = models.DateTimeField(null=True, blank=True)
    restaurado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='backups_restaurados'
    )
    notas_restauracion = models.TextField(blank=True)

    # Metadatos
    version_django = models.CharField(max_length=20, blank=True)
    version_python = models.CharField(max_length=20, blank=True)
    metadatos = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Copia de Seguridad"
        verbose_name_plural = "Copias de Seguridad"
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['fecha_creacion']),
            models.Index(fields=['estado']),
            models.Index(fields=['creado_por']),
        ]


class CentroFormacion(models.Model):
    nombre      = models.CharField(max_length=200, unique=True)
    codigo      = models.CharField(max_length=20, blank=True)
    direccion   = models.CharField(max_length=300, blank=True)
    telefono    = models.CharField(max_length=30, blank=True)
    email       = models.EmailField(blank=True)
    descripcion = models.TextField(blank=True)
    activo      = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Centro de Formación"
        verbose_name_plural = "Centros de Formación"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class AmbienteFormacion(models.Model):
    centro      = models.ForeignKey(CentroFormacion, on_delete=models.CASCADE, related_name='ambientes')
    nombre      = models.CharField(max_length=200)
    codigo      = models.CharField(max_length=20, blank=True)
    capacidad   = models.PositiveIntegerField(default=0)
    descripcion = models.TextField(blank=True)
    activo      = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ambiente de Formación"
        verbose_name_plural = "Ambientes de Formación"
        ordering = ['centro', 'nombre']
        unique_together = [['centro', 'nombre']]

    def __str__(self):
        return f"{self.nombre} — {self.centro.nombre}"

    def __str__(self):
        return f"Backup: {self.nombre} ({self.get_estado_display()})"

    @property
    def tamaño_mb(self):
        """Retorna el tamaño en MB"""
        return round(self.tamaño_bytes / (1024 * 1024), 2)

    @property
    def puede_restaurar(self):
        """Verifica si el backup puede ser restaurado"""
        import os
        tiene_archivo = bool(self.archivo) or (self.ruta_archivo and os.path.exists(self.ruta_archivo))
        return self.estado == 'completado' and tiene_archivo

    @property
    def metadata_json(self):
        """Retorna los metadatos en formato JSON legible"""
        import json
        return json.dumps(self.metadatos, indent=2, ensure_ascii=False) if self.metadatos else '{}'
