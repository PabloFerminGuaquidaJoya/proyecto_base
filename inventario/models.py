from django.db import models
from django.core.validators import MinValueValidator
from usuarios.models import Usuario


class PiezaInventario(models.Model):
    CONDICION_CHOICES = [
        ('nueva',     'Nueva'),
        ('usada',     'Usada'),
        ('cambiada',  'Cambiada'),
        ('dañada',    'Dañada'),
    ]

    # Identificación
    codigo_inventario   = models.CharField(max_length=50, unique=True)
    nombre              = models.CharField(max_length=200)
    numero_serie        = models.CharField(max_length=100, unique=True, blank=True)
    numero_factura      = models.CharField(max_length=100, blank=True)

    # Clasificación
    categoria   = models.CharField(max_length=100, blank=True)
    marca       = models.CharField(max_length=100, blank=True)
    modelo      = models.CharField(max_length=100, blank=True)

    # Características físicas
    peso        = models.CharField(max_length=50, blank=True, help_text='Ej: 12.5 kg')
    dimensiones = models.CharField(max_length=150, blank=True, help_text='Ej: 30x20x15 cm')

    # Ubicación y responsabilidad
    centro_formacion    = models.CharField(max_length=200, blank=True)
    ambiente_formacion  = models.CharField(max_length=200, blank=True)
    ubicacion           = models.CharField(max_length=200, blank=True)
    responsable         = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='piezas_responsable'
    )

    # Adquisición
    proveedor           = models.CharField(max_length=200, blank=True)
    valor_adquisicion   = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)]
    )
    garantia_meses      = models.PositiveIntegerField(default=0)

    # Uso
    horas_uso           = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        validators=[MinValueValidator(0)]
    )
    horas_uso_maximas   = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)]
    )

    # Estado
    condicion = models.CharField(max_length=20, choices=CONDICION_CHOICES, default='nueva')

    # Fotos
    foto_pieza    = models.ImageField(
        upload_to='inventario/piezas/', blank=True, null=True,
        help_text='Fotografía de la pieza'
    )
    foto_empaque  = models.ImageField(
        upload_to='inventario/empaques/', blank=True, null=True,
        help_text='Fotografía del empaque'
    )

    # Detalles técnicos
    especificaciones_tecnicas = models.TextField(blank=True)
    observaciones             = models.TextField(blank=True)

    # Metadatos
    fecha_registro  = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    registrado_por  = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='piezas_registradas'
    )

    class Meta:
        verbose_name = 'Pieza de Inventario'
        verbose_name_plural = 'Piezas de Inventario'
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['codigo_inventario']),
            models.Index(fields=['condicion']),
        ]

    def __str__(self):
        return f'{self.codigo_inventario} – {self.nombre}'

    @property
    def tiene_alerta(self):
        """True si superó las horas máximas o está dañada."""
        if self.condicion == 'dañada':
            return True
        if self.horas_uso_maximas and self.horas_uso >= self.horas_uso_maximas:
            return True
        return False
