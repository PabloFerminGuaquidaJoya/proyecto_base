from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
import uuid

class CategoriaMaquina(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    icono = models.CharField(max_length=50, default='bi-gear')
    color = models.CharField(max_length=7, default='#007bff', help_text="Color en formato hexadecimal")
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoría de Máquina"
        verbose_name_plural = "Categorías de Máquinas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    nombre = models.CharField(max_length=200)
    nit = models.CharField(max_length=20, unique=True)
    contacto_nombre = models.CharField(max_length=100)
    contacto_telefono = models.CharField(max_length=20)
    contacto_email = models.EmailField()
    direccion = models.TextField()
    ciudad = models.CharField(max_length=100)
    pais = models.CharField(max_length=100, default='Colombia')
    sitio_web = models.URLField(blank=True)
    calificacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Maquina(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('operativa', 'Operativa'),
        ('mantenimiento', 'En Mantenimiento'),
        ('reparacion', 'En Reparación'),
        ('fuera_servicio', 'Fuera de Servicio'),
        ('retirada', 'Retirada'),
    ]

    CONDICION_CHOICES = [
        ('excelente', 'Excelente'),
        ('buena', 'Buena'),
        ('regular', 'Regular'),
        ('mala', 'Mala'),
        ('critica', 'Crítica'),
    ]

    # Información básica
    codigo_inventario = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(CategoriaMaquina, on_delete=models.PROTECT)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    numero_serie = models.CharField(max_length=100, unique=True)

    # Estado y condición
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    condicion = models.CharField(max_length=20, choices=CONDICION_CHOICES, default='excelente')

    # Especificaciones técnicas
    especificaciones_tecnicas = models.TextField(blank=True)
    capacidad = models.CharField(max_length=200, blank=True)
    potencia = models.CharField(max_length=100, blank=True)
    voltaje = models.CharField(max_length=50, blank=True)
    dimensiones = models.CharField(max_length=100, blank=True)
    peso = models.CharField(max_length=50, blank=True)

    # Ubicación
    ubicacion = models.CharField(max_length=200)
    centro_formacion = models.CharField(max_length=200)
    ambiente_formacion = models.CharField(max_length=200, blank=True)
    responsable = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='maquinas_asignadas'
    )

    # Información de compra
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_adquisicion = models.DateField()
    valor_adquisicion = models.DecimalField(max_digits=15, decimal_places=2)
    numero_factura = models.CharField(max_length=100, blank=True)
    garantia_meses = models.IntegerField(default=12)

    # Datos de uso
    horas_uso_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    horas_uso_mes = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    eficiencia = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=100, help_text="Porcentaje de eficiencia"
    )

    # Mantenimiento
    fecha_ultimo_mantenimiento = models.DateField(null=True, blank=True)
    proximo_mantenimiento = models.DateField(null=True, blank=True)
    frecuencia_mantenimiento_dias = models.IntegerField(default=90)

    # Archivos y documentos
    imagen = models.ImageField(upload_to='maquinaria/imagenes/', blank=True, null=True)
    manual_pdf = models.FileField(upload_to='maquinaria/manuales/', blank=True, null=True)
    ficha_tecnica = models.FileField(upload_to='maquinaria/fichas/', blank=True, null=True)

    # Metadatos
    observaciones = models.TextField(blank=True)
    qr_code = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='maquinas_creadas'
    )

    class Meta:
        verbose_name = "Máquina"
        verbose_name_plural = "Máquinas"
        ordering = ['codigo_inventario']
        indexes = [
            models.Index(fields=['codigo_inventario']),
            models.Index(fields=['estado']),
            models.Index(fields=['categoria']),
            models.Index(fields=['centro_formacion']),
        ]

    def __str__(self):
        return f"{self.codigo_inventario} - {self.nombre}"

    def get_absolute_url(self):
        return reverse('maquinaria:detalle', kwargs={'pk': self.pk})

    @property
    def necesita_mantenimiento(self):
        if not self.proximo_mantenimiento:
            return False
        from django.utils import timezone
        return self.proximo_mantenimiento <= timezone.now().date()

    @property
    def tiempo_sin_mantenimiento(self):
        if not self.fecha_ultimo_mantenimiento:
            return None
        from django.utils import timezone
        return (timezone.now().date() - self.fecha_ultimo_mantenimiento).days

class AlertaMaquina(models.Model):
    TIPO_CHOICES = [
        ('mantenimiento', 'Mantenimiento Programado'),
        ('reparacion', 'Reparación Urgente'),
        ('eficiencia', 'Baja Eficiencia'),
        ('uso_excesivo', 'Uso Excesivo'),
        ('garantia', 'Garantía por Vencer'),
        ('inspeccion', 'Inspección Requerida'),
    ]

    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]

    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('en_proceso', 'En Proceso'),
        ('resuelta', 'Resuelta'),
        ('ignorada', 'Ignorada'),
    ]

    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE, related_name='alertas')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activa')

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    resuelto_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='alertas_resueltas'
    )

    notas_resolucion = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='alertas_creadas'
    )

    class Meta:
        verbose_name = "Alerta de Máquina"
        verbose_name_plural = "Alertas de Máquinas"
        ordering = ['-fecha_creacion', '-prioridad']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['prioridad']),
            models.Index(fields=['tipo']),
        ]

    def __str__(self):
        return f"{self.maquina.codigo_inventario} - {self.titulo}"

class HistorialMaquina(models.Model):
    TIPO_EVENTO_CHOICES = [
        ('creacion', 'Creación'),
        ('mantenimiento', 'Mantenimiento'),
        ('reparacion', 'Reparación'),
        ('cambio_estado', 'Cambio de Estado'),
        ('cambio_ubicacion', 'Cambio de Ubicación'),
        ('cambio_responsable', 'Cambio de Responsable'),
        ('actualizacion', 'Actualización de Datos'),
        ('inspeccion', 'Inspección'),
        ('alerta_creada', 'Alerta Creada'),
        ('alerta_resuelta', 'Alerta Resuelta'),
        ('eliminacion', 'Eliminación'),
    ]

    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE, related_name='historial')
    tipo_evento = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES)
    descripcion = models.TextField()
    valor_anterior = models.TextField(blank=True)
    valor_nuevo = models.TextField(blank=True)
    costo_asociado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    fecha_evento = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    archivos_adjuntos = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = "Historial de Máquina"
        verbose_name_plural = "Historiales de Máquinas"
        ordering = ['-fecha_evento']
        indexes = [
            models.Index(fields=['maquina', '-fecha_evento']),
            models.Index(fields=['tipo_evento']),
        ]

    def __str__(self):
        return f"{self.maquina.codigo_inventario} - {self.get_tipo_evento_display()} ({self.fecha_evento})"

class MantenimientoProgramado(models.Model):
    TIPO_MANTENIMIENTO_CHOICES = [
        ('preventivo', 'Preventivo'),
        ('correctivo', 'Correctivo'),
        ('predictivo', 'Predictivo'),
        ('urgente', 'Urgente'),
        ('emergencia', 'Emergencia'),
    ]

    ESTADO_CHOICES = [
        ('programado', 'Programado'),
        ('en_progreso', 'En Progreso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
        ('postergado', 'Postergado'),
    ]

    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
        ('emergencia', 'Emergencia'),
    ]

    # Información básica
    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE, related_name='mantenimientos')
    tipo = models.CharField(max_length=20, choices=TIPO_MANTENIMIENTO_CHOICES)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='media')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='programado')

    # Fechas y tiempos
    fecha_programada = models.DateTimeField()
    fecha_inicio_real = models.DateTimeField(null=True, blank=True)
    fecha_fin_real = models.DateTimeField(null=True, blank=True)
    duracion_estimada = models.DurationField(help_text="Duración estimada en formato HH:MM:SS")
    duracion_real = models.DurationField(null=True, blank=True)

    # Personal y recursos
    tecnico_asignado = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mantenimientos_asignados'
    )
    tecnico_realizado = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mantenimientos_realizados'
    )

    # Detalles técnicos
    componentes_revisar = models.JSONField(default=list, help_text="Lista de componentes a revisar")
    herramientas_necesarias = models.JSONField(default=list, help_text="Herramientas necesarias")
    repuestos_necesarios = models.JSONField(default=list, help_text="Repuestos necesarios")
    procedimientos = models.TextField(blank=True, help_text="Procedimientos paso a paso")

    # Resultados y observaciones
    trabajo_realizado = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)
    problemas_encontrados = models.TextField(blank=True)
    repuestos_utilizados = models.JSONField(default=list)
    tiempo_parada = models.DurationField(null=True, blank=True, help_text="Tiempo que la máquina estuvo parada")

    # Costos
    costo_estimado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    costo_real = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    costo_repuestos = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    costo_mano_obra = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Próximo mantenimiento
    proximo_mantenimiento = models.DateField(null=True, blank=True)
    horas_operacion_siguiente = models.PositiveIntegerField(null=True, blank=True)

    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='mantenimientos_creados'
    )

    class Meta:
        verbose_name = "Mantenimiento Programado"
        verbose_name_plural = "Mantenimientos Programados"
        ordering = ['fecha_programada']
        indexes = [
            models.Index(fields=['fecha_programada']),
            models.Index(fields=['estado']),
            models.Index(fields=['tipo']),
            models.Index(fields=['prioridad']),
        ]

    def __str__(self):
        return f"{self.maquina.codigo_inventario} - {self.titulo} ({self.fecha_programada.strftime('%d/%m/%Y')})"

    @property
    def esta_vencido(self):
        from django.utils import timezone
        return self.fecha_programada < timezone.now() and self.estado == 'programado'

    @property
    def duracion_display(self):
        if self.duracion_real:
            return self.duracion_real
        return self.duracion_estimada

    def marcar_completado(self, usuario=None):
        from django.utils import timezone
        self.estado = 'completado'
        self.fecha_fin_real = timezone.now()
        if usuario:
            self.tecnico_realizado = usuario
        self.save()

        # Crear entrada en historial
        HistorialMaquina.objects.create(
            maquina=self.maquina,
            tipo_evento='mantenimiento',
            descripcion=f'Mantenimiento completado: {self.titulo}',
            usuario=usuario
        )

class MaquinaEliminada(models.Model):
    """
    Modelo para guardar el registro completo de máquinas eliminadas
    con toda su información histórica
    """
    # Información básica de la máquina eliminada
    codigo_inventario = models.CharField(max_length=50)
    nombre = models.CharField(max_length=200)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    numero_serie = models.CharField(max_length=100)
    categoria_nombre = models.CharField(max_length=100)

    # Estado al momento de eliminación
    estado_final = models.CharField(max_length=20)
    condicion_final = models.CharField(max_length=20)
    ubicacion = models.CharField(max_length=200)
    centro_formacion = models.CharField(max_length=200)

    # Datos de uso
    horas_uso_total = models.DecimalField(max_digits=10, decimal_places=2)
    eficiencia_final = models.DecimalField(max_digits=5, decimal_places=2)

    # Datos completos en JSON
    datos_completos_maquina = models.JSONField(
        help_text="Todos los datos de la máquina en formato JSON"
    )
    historial_completo = models.JSONField(
        default=list,
        help_text="Todo el historial de eventos de la máquina"
    )
    alertas_asociadas = models.JSONField(
        default=list,
        help_text="Todas las alertas que tuvo la máquina"
    )
    mantenimientos_realizados = models.JSONField(
        default=list,
        help_text="Historial completo de mantenimientos"
    )

    # Información de eliminación
    fecha_eliminacion = models.DateTimeField(auto_now_add=True)
    eliminado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='maquinas_eliminadas'
    )
    motivo_eliminacion = models.TextField(blank=True)
    observaciones_finales = models.TextField(blank=True)

    # Estadísticas resumidas
    total_mantenimientos = models.IntegerField(default=0)
    total_reparaciones = models.IntegerField(default=0)
    total_alertas = models.IntegerField(default=0)
    costo_total_mantenimiento = models.DecimalField(
        max_digits=15, decimal_places=2, default=0
    )
    dias_operacion = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Máquina Eliminada"
        verbose_name_plural = "Máquinas Eliminadas"
        ordering = ['-fecha_eliminacion']
        indexes = [
            models.Index(fields=['codigo_inventario']),
            models.Index(fields=['fecha_eliminacion']),
        ]

    def __str__(self):
        return f"{self.codigo_inventario} - {self.nombre} (Eliminada: {self.fecha_eliminacion.strftime('%d/%m/%Y')})"
