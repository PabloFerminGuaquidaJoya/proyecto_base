from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class TipoReporte(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField()
    template_path = models.CharField(max_length=200, blank=True)
    parametros_requeridos = models.JSONField(default=list)
    formato_salida = models.JSONField(default=list)  # ['pdf', 'excel', 'csv']
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tipo de Reporte"
        verbose_name_plural = "Tipos de Reporte"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Reporte(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('generando', 'Generando'),
        ('completado', 'Completado'),
        ('error', 'Error'),
        ('cancelado', 'Cancelado'),
    ]

    FORMATO_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo_reporte = models.ForeignKey(TipoReporte, on_delete=models.PROTECT)
    usuario_solicitante = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        related_name='reportes_solicitados'
    )

    # Configuración del reporte
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    parametros = models.JSONField(default=dict)
    formato = models.CharField(max_length=10, choices=FORMATO_CHOICES, default='pdf')

    # Filtros aplicados
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    centros_formacion = models.JSONField(default=list, blank=True)
    categorias_maquina = models.JSONField(default=list, blank=True)
    estados_maquina = models.JSONField(default=list, blank=True)

    # Estado y procesamiento
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_inicio_procesamiento = models.DateTimeField(null=True, blank=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    tiempo_procesamiento = models.DurationField(null=True, blank=True)

    # Resultados
    archivo_resultado = models.FileField(
        upload_to='reportes/resultados/',
        blank=True, null=True
    )
    url_descarga = models.URLField(blank=True)
    tamaño_archivo = models.BigIntegerField(null=True, blank=True)
    total_registros = models.IntegerField(null=True, blank=True)

    # Metadatos
    error_mensaje = models.TextField(blank=True)
    logs_procesamiento = models.JSONField(default=list, blank=True)
    veces_descargado = models.IntegerField(default=0)
    fecha_ultima_descarga = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"
        ordering = ['-fecha_solicitud']
        indexes = [
            models.Index(fields=['usuario_solicitante', '-fecha_solicitud']),
            models.Index(fields=['estado']),
            models.Index(fields=['tipo_reporte']),
        ]

    def __str__(self):
        return f"{self.titulo} - {self.usuario_solicitante.nombre_completo}"

class MetricasRendimiento(models.Model):
    PERIODO_CHOICES = [
        ('diario', 'Diario'),
        ('semanal', 'Semanal'),
        ('mensual', 'Mensual'),
        ('anual', 'Anual'),
    ]

    # Identificación
    fecha = models.DateField()
    periodo = models.CharField(max_length=10, choices=PERIODO_CHOICES)
    centro_formacion = models.CharField(max_length=200)
    categoria_maquina = models.ForeignKey(
        'maquinaria.CategoriaMaquina',
        on_delete=models.CASCADE,
        null=True, blank=True
    )

    # Métricas operacionales
    total_maquinas = models.IntegerField(default=0)
    maquinas_operativas = models.IntegerField(default=0)
    maquinas_mantenimiento = models.IntegerField(default=0)
    maquinas_reparacion = models.IntegerField(default=0)
    maquinas_fuera_servicio = models.IntegerField(default=0)

    # Métricas de eficiencia
    eficiencia_promedio = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )
    horas_uso_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    horas_disponibles = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tiempo_inactividad = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Métricas de mantenimiento
    mantenimientos_programados = models.IntegerField(default=0)
    mantenimientos_completados = models.IntegerField(default=0)
    mantenimientos_pendientes = models.IntegerField(default=0)
    tiempo_promedio_reparacion = models.DecimalField(
        max_digits=8, decimal_places=2, default=0
    )

    # Métricas financieras
    costo_mantenimiento_total = models.DecimalField(
        max_digits=15, decimal_places=2, default=0
    )
    costo_reparaciones = models.DecimalField(
        max_digits=15, decimal_places=2, default=0
    )
    valor_maquinaria_total = models.DecimalField(
        max_digits=20, decimal_places=2, default=0
    )

    # Métricas de alertas
    alertas_generadas = models.IntegerField(default=0)
    alertas_resueltas = models.IntegerField(default=0)
    alertas_criticas = models.IntegerField(default=0)

    # Control
    fecha_calculo = models.DateTimeField(auto_now_add=True)
    actualizado_por_sistema = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Métricas de Rendimiento"
        verbose_name_plural = "Métricas de Rendimiento"
        ordering = ['-fecha', 'centro_formacion']
        unique_together = ['fecha', 'periodo', 'centro_formacion', 'categoria_maquina']
        indexes = [
            models.Index(fields=['fecha', 'periodo']),
            models.Index(fields=['centro_formacion']),
            models.Index(fields=['categoria_maquina']),
        ]

    def __str__(self):
        return f"Métricas {self.periodo} - {self.centro_formacion} ({self.fecha})"

    @property
    def porcentaje_disponibilidad(self):
        if self.total_maquinas == 0:
            return 0
        return (self.maquinas_operativas / self.total_maquinas) * 100

    @property
    def tasa_cumplimiento_mantenimiento(self):
        if self.mantenimientos_programados == 0:
            return 100
        return (self.mantenimientos_completados / self.mantenimientos_programados) * 100
