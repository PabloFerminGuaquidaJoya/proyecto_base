from django import forms
from .models import Reporte, TipoReporte, MetricasRendimiento
from maquinaria.models import CategoriaMaquina

class GenerarReporteForm(forms.ModelForm):
    class Meta:
        model = Reporte
        fields = [
            'tipo_reporte', 'titulo', 'descripcion', 'formato',
            'fecha_inicio', 'fecha_fin', 'centros_formacion',
            'categorias_maquina', 'estados_maquina', 'parametros'
        ]
        widgets = {
            'tipo_reporte': forms.Select(attrs={
                'class': 'form-select'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del reporte'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción opcional del reporte...'
            }),
            'formato': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'parametros': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Parámetros adicionales en formato JSON (opcional)'
            })
        }

    centros_formacion_choices = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        help_text='Seleccionar centros a incluir'
    )

    categorias_maquina_choices = forms.ModelMultipleChoiceField(
        queryset=CategoriaMaquina.objects.filter(activa=True),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        help_text='Seleccionar categorías a incluir'
    )

    estados_maquina_choices = forms.MultipleChoiceField(
        choices=[
            ('disponible', 'Disponible'),
            ('operativa', 'Operativa'),
            ('mantenimiento', 'En Mantenimiento'),
            ('reparacion', 'En Reparación'),
            ('fuera_servicio', 'Fuera de Servicio'),
        ],
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        help_text='Seleccionar estados a incluir'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate centros choices dynamically
        from maquinaria.models import Maquina
        centros = Maquina.objects.values_list('centro_formacion', flat=True).distinct()
        self.fields['centros_formacion_choices'].choices = [(c, c) for c in centros if c]

class TipoReporteForm(forms.ModelForm):
    class Meta:
        model = TipoReporte
        fields = ['nombre', 'descripcion', 'template_path', 'parametros_requeridos', 'formato_salida', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del tipo de reporte'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del tipo de reporte...'
            }),
            'template_path': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ruta del template (opcional)'
            }),
            'parametros_requeridos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Lista de parámetros en formato JSON'
            }),
            'formato_salida': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': '["pdf", "excel", "csv"]'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class FiltroReportesForm(forms.Form):
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    periodo = forms.ChoiceField(
        choices=[
            ('', 'Personalizado'),
            ('last-7-days', 'Últimos 7 días'),
            ('last-30-days', 'Últimos 30 días'),
            ('last-3-months', 'Últimos 3 meses'),
            ('last-year', 'Último año'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    centro_formacion = forms.ChoiceField(
        choices=[('', 'Todos los centros')],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    categoria_maquina = forms.ModelChoiceField(
        queryset=CategoriaMaquina.objects.filter(activa=True),
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate centros choices
        from maquinaria.models import Maquina
        centros = Maquina.objects.values_list('centro_formacion', flat=True).distinct()
        choices = [('', 'Todos los centros')] + [(c, c) for c in centros if c]
        self.fields['centro_formacion'].choices = choices

class ExportarDashboardForm(forms.Form):
    FORMATO_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('png', 'Imagen PNG')
    ]

    formato = forms.ChoiceField(
        choices=FORMATO_CHOICES,
        initial='pdf',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    incluir_graficos = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    incluir_tablas = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    incluir_kpis = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

class PersonalizarDashboardForm(forms.Form):
    widgets_seleccionados = forms.MultipleChoiceField(
        choices=[
            ('kpi-eficiencia', 'KPI Eficiencia Global'),
            ('kpi-costos', 'KPI Costos Mantenimiento'),
            ('kpi-downtime', 'KPI Tiempo Fuera'),
            ('kpi-satisfaccion', 'KPI Satisfacción Usuario'),
            ('grafico-eficiencia', 'Gráfico Eficiencia Temporal'),
            ('grafico-estados', 'Gráfico Estados Máquinas'),
            ('grafico-costos', 'Gráfico Costos por Categoría'),
            ('tabla-maquinas', 'Tabla Detalle Máquinas'),
            ('alertas-activas', 'Panel Alertas Activas'),
            ('mantenimientos-proximos', 'Próximos Mantenimientos'),
        ],
        widget=forms.CheckboxSelectMultiple(),
        help_text='Selecciona los widgets a mostrar en tu dashboard'
    )
    tema_colores = forms.ChoiceField(
        choices=[
            ('azul', 'Azul SENA'),
            ('verde', 'Verde Corporativo'),
            ('gris', 'Gris Profesional'),
            ('personalizado', 'Personalizado')
        ],
        initial='azul',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    actualizacion_automatica = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Actualizar datos automáticamente cada 30 segundos'
    )

class AnalisisTendenciasForm(forms.Form):
    """Formulario para configurar análisis de tendencias"""
    metrica = forms.ChoiceField(
        choices=[
            ('eficiencia', 'Eficiencia Operativa'),
            ('costos', 'Costos de Mantenimiento'),
            ('downtime', 'Tiempo de Inactividad'),
            ('alertas', 'Número de Alertas'),
            ('uso_horas', 'Horas de Uso')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    periodo_analisis = forms.ChoiceField(
        choices=[
            ('6m', '6 meses'),
            ('12m', '12 meses'),
            ('24m', '24 meses'),
            ('personalizado', 'Personalizado')
        ],
        initial='12m',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    agrupacion = forms.ChoiceField(
        choices=[
            ('diario', 'Diario'),
            ('semanal', 'Semanal'),
            ('mensual', 'Mensual'),
            ('trimestral', 'Trimestral')
        ],
        initial='mensual',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    categorias_incluir = forms.ModelMultipleChoiceField(
        queryset=CategoriaMaquina.objects.filter(activa=True),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        help_text='Dejar vacío para incluir todas las categorías'
    )

class AnalisisComparativoForm(forms.Form):
    """Formulario para análisis comparativo entre períodos"""
    periodo_base = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Q1 2024'
        })
    )
    fecha_inicio_base = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    fecha_fin_base = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    periodo_comparacion = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Q2 2024'
        })
    )
    fecha_inicio_comparacion = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    fecha_fin_comparacion = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    metricas_comparar = forms.MultipleChoiceField(
        choices=[
            ('eficiencia', 'Eficiencia Promedio'),
            ('costos', 'Costos Totales'),
            ('downtime', 'Tiempo de Inactividad'),
            ('mantenimientos', 'Mantenimientos Realizados'),
            ('alertas', 'Alertas Generadas'),
            ('disponibilidad', 'Disponibilidad de Máquinas')
        ],
        widget=forms.CheckboxSelectMultiple(),
        initial=['eficiencia', 'costos', 'disponibilidad']
    )

class ConfiguracionReportesForm(forms.Form):
    """Formulario para configurar sistema de reportes"""
    ruta_almacenamiento = forms.CharField(
        initial='reportes/generados/',
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
        help_text='Ruta donde se almacenan los reportes generados'
    )
    tiempo_retencion_dias = forms.IntegerField(
        initial=90,
        min_value=7,
        max_value=365,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        }),
        help_text='Días que se mantienen los reportes antes de eliminarse automáticamente'
    )
    tamaño_maximo_mb = forms.IntegerField(
        initial=50,
        min_value=1,
        max_value=500,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        }),
        help_text='Tamaño máximo permitido para reportes (MB)'
    )
    permitir_programacion = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Permitir programación de reportes automáticos'
    )
    notificar_completado = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Notificar por email cuando un reporte esté listo'
    )

class ReporteProgramadoForm(forms.Form):
    """Formulario para programar reportes automáticos"""
    tipo_reporte = forms.ModelChoiceField(
        queryset=TipoReporte.objects.filter(activo=True),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    frecuencia = forms.ChoiceField(
        choices=[
            ('diario', 'Diario'),
            ('semanal', 'Semanal'),
            ('mensual', 'Mensual'),
            ('trimestral', 'Trimestral')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    hora_ejecucion = forms.TimeField(
        initial='06:00',
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    email_destinatarios = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Emails separados por comas'
        }),
        help_text='Emails que recibirán el reporte automáticamente'
    )
    activo = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )