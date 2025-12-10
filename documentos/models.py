from django.db import models
from django.core.validators import FileExtensionValidator
import uuid
import os

class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    extensiones_permitidas = models.JSONField(default=list)  # ['.pdf', '.doc', '.docx']
    tamaño_maximo_mb = models.IntegerField(default=50)
    icono = models.CharField(max_length=50, default='bi-file-text')
    color = models.CharField(max_length=7, default='#007bff')
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tipo de Documento"
        verbose_name_plural = "Tipos de Documento"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class CategoriaDocumento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='subcategorias'
    )
    icono = models.CharField(max_length=50, default='bi-folder')
    color = models.CharField(max_length=7, default='#ffc107')
    orden = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Categoría de Documento"
        verbose_name_plural = "Categorías de Documento"
        ordering = ['orden', 'nombre']

    def __str__(self):
        if self.parent:
            return f"{self.parent.nombre} > {self.nombre}"
        return self.nombre

    @property
    def nivel(self):
        if self.parent:
            return self.parent.nivel + 1
        return 0

def documento_upload_path(instance, filename):
    # Organizar archivos por año/mes/categoria/
    from django.utils import timezone
    fecha = instance.fecha_creacion if instance.fecha_creacion else timezone.now()
    categoria = instance.categoria.nombre.lower().replace(' ', '_') if instance.categoria else 'general'
    return f'documentos/{fecha.year}/{fecha.month:02d}/{categoria}/{filename}'

class Documento(models.Model):
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('revision', 'En Revisión'),
        ('aprobado', 'Aprobado'),
        ('publicado', 'Publicado'),
        ('archivado', 'Archivado'),
        ('obsoleto', 'Obsoleto'),
    ]

    NIVEL_ACCESO_CHOICES = [
        ('publico', 'Público'),
        ('interno', 'Interno'),
        ('confidencial', 'Confidencial'),
        ('restringido', 'Restringido'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Información básica
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.PROTECT)
    categoria = models.ForeignKey(CategoriaDocumento, on_delete=models.PROTECT)

    # Archivo
    archivo = models.FileField(
        upload_to=documento_upload_path,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'xlsx', 'xls', 'ppt', 'pptx']
        )]
    )
    tamaño_archivo = models.BigIntegerField(null=True, blank=True)
    checksum = models.CharField(max_length=64, blank=True)

    # Metadatos
    version = models.CharField(max_length=20, default='1.0')
    palabras_clave = models.JSONField(default=list, blank=True)
    autor_original = models.CharField(max_length=200, blank=True)

    # Control de acceso
    nivel_acceso = models.CharField(
        max_length=15,
        choices=NIVEL_ACCESO_CHOICES,
        default='interno'
    )
    usuarios_acceso = models.ManyToManyField(
        'usuarios.Usuario',
        blank=True,
        related_name='documentos_acceso'
    )

    # Estado y fechas
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='borrador')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    fecha_publicacion = models.DateTimeField(null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)

    # Relaciones
    creado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        related_name='documentos_creados'
    )
    modificado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='documentos_modificados'
    )
    maquina_relacionada = models.ForeignKey(
        'maquinaria.Maquina',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='documentos'
    )

    # Estadísticas
    total_descargas = models.IntegerField(default=0)
    total_visualizaciones = models.IntegerField(default=0)
    ultima_descarga = models.DateTimeField(null=True, blank=True)

    # Contenido indexado para búsqueda
    contenido_texto = models.TextField(blank=True)
    indices_busqueda = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ['-fecha_modificacion']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['categoria']),
            models.Index(fields=['tipo_documento']),
            models.Index(fields=['creado_por']),
            models.Index(fields=['nivel_acceso']),
            models.Index(fields=['maquina_relacionada']),
        ]

    def __str__(self):
        return f"{self.titulo} v{self.version}"

    @property
    def extension(self):
        return os.path.splitext(self.archivo.name)[1].lower()

    @property
    def tamaño_mb(self):
        if self.tamaño_archivo:
            return round(self.tamaño_archivo / (1024 * 1024), 2)
        return 0

    def save(self, *args, **kwargs):
        if self.archivo and not self.tamaño_archivo:
            self.tamaño_archivo = self.archivo.size
        super().save(*args, **kwargs)
