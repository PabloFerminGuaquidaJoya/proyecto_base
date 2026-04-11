from django import forms
from django.core.validators import RegexValidator
from .models import Maquina, CategoriaMaquina, Proveedor, AlertaMaquina, HistorialMaquina, ObjetoMaquinaria, UsoMaquinaria
from usuarios.models import Usuario

class MaquinaForm(forms.ModelForm):
    class Meta:
        model = Maquina
        exclude = ['created_at', 'updated_at', 'created_by', 'qr_code']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la máquina'
            }),
            'codigo_inventario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: TOR-001'
            }),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Marca del equipo'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Modelo del equipo'
            }),
            'numero_serie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de serie único'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'especificaciones_tecnicas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Especificaciones técnicas detalladas...'
            }),
            'capacidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 500 kg, 10 HP'
            }),
            'potencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 15 HP, 11 kW'
            }),
            'voltaje': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 220V, 440V'
            }),
            'dimensiones': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Largo x Ancho x Alto (cm)'
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Ej: 3500.00'
            }),
            'ubicacion': forms.HiddenInput(),
            'centro_formacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Centro de formación'
            }),
            'ambiente_formacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Taller 3, Laboratorio de Hidráulica'
            }),
            'proveedor': forms.Select(attrs={
                'class': 'form-select'
            }),
            'responsable': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_adquisicion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'valor_adquisicion': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'numero_factura': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de factura'
            }),
            'garantia_meses': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '120'
            }),
            'horas_uso_total': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0'
            }),
            'horas_uso_mes': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0'
            }),
            'fecha_ultimo_mantenimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'proximo_mantenimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'frecuencia_mantenimiento_dias': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '365'
            }),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'manual_pdf': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
            'ficha_tecnica': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Observaciones técnicas adicionales (especificaciones, notas de mantenimiento, etc.)...'
            })
        }

    labels = {
        'ambiente_formacion': 'Ambiente / Taller',
        'peso': 'Peso (kg)',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer ciertos campos requeridos
        self.fields['nombre'].required = True
        self.fields['codigo_inventario'].required = True
        self.fields['categoria'].required = True
        self.fields['marca'].required = True
        self.fields['modelo'].required = True
        self.fields['numero_serie'].required = True
        self.fields['fecha_adquisicion'].required = True
        self.fields['valor_adquisicion'].required = True

        # ubicacion se llena automáticamente desde ambiente_formacion
        self.fields['ubicacion'].required = False
        self.fields['ambiente_formacion'].required = True
        self.fields['ambiente_formacion'].label = 'Ambiente / Taller'
        self.fields['peso'].label = 'Peso (kg)'
        self.fields['observaciones'].label = 'Observaciones técnicas adicionales'

        # Filtrar proveedores activos
        self.fields['proveedor'].queryset = Proveedor.objects.filter(activo=True)

        # Si la máquina ya existe y tiene fecha de adquisición, bloquear el campo
        if self.instance.pk and self.instance.fecha_adquisicion:
            self.fields['fecha_adquisicion'].widget.attrs['readonly'] = True
            self.fields['fecha_adquisicion'].widget.attrs['class'] = 'form-control bg-light'
            self.fields['fecha_adquisicion'].help_text = 'La fecha de adquisición no puede modificarse una vez establecida.'

    def clean_fecha_adquisicion(self):
        # Si la máquina ya tiene fecha de adquisición, ignorar el valor enviado y conservar el original
        if self.instance.pk and self.instance.fecha_adquisicion:
            return self.instance.fecha_adquisicion
        return self.cleaned_data.get('fecha_adquisicion')

    def clean(self):
        cleaned_data = super().clean()
        # Sincronizar ubicacion con ambiente_formacion para mantener compatibilidad
        ambiente = cleaned_data.get('ambiente_formacion', '')
        if ambiente:
            cleaned_data['ubicacion'] = ambiente
        return cleaned_data

class CategoriaMaquinaForm(forms.ModelForm):
    class Meta:
        model = CategoriaMaquina
        fields = ['nombre', 'descripcion', 'icono', 'color', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la categoría...'
            }),
            'icono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: bi-gear, bi-wrench',
                'data-toggle': 'tooltip',
                'title': 'Icono Bootstrap (ej: bi-gear)'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'activa': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            'nombre', 'nit', 'contacto_nombre', 'contacto_telefono',
            'contacto_email', 'direccion', 'ciudad', 'pais',
            'sitio_web', 'calificacion', 'activo'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la empresa'
            }),
            'nit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '900.123.456-7'
            }),
            'contacto_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del contacto principal'
            }),
            'contacto_telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+57 300 123 4567'
            }),
            'contacto_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contacto@empresa.com'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Dirección completa'
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad'
            }),
            'pais': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'País'
            }),
            'sitio_web': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.empresa.com'
            }),
            'calificacion': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[(i, f'{i} estrella{"s" if i != 1 else ""}') for i in range(1, 6)]),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class AlertaMaquinaForm(forms.ModelForm):
    class Meta:
        model = AlertaMaquina
        exclude = ['fecha_creacion', 'fecha_resolucion', 'resuelto_por', 'created_by']
        widgets = {
            'maquina': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la alerta'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada de la alerta...'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

class BuscarMaquinasForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por código, nombre, marca...',
            'autocomplete': 'off'
        })
    )
    categoria = forms.ModelChoiceField(
        queryset=CategoriaMaquina.objects.filter(activa=True),
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Maquina.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    centro_formacion = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Centro de formación'
        })
    )

class FiltroMantenimientoForm(forms.Form):
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
    categoria = forms.ModelChoiceField(
        queryset=CategoriaMaquina.objects.filter(activa=True),
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    urgente_solamente = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

class CambiarEstadoForm(forms.Form):
    estado = forms.ChoiceField(
        choices=Maquina.ESTADO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Observaciones sobre el cambio de estado...'
        })
    )

class ResolverAlertaForm(forms.Form):
    notas_resolucion = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Describe cómo se resolvió la alerta...'
        })
    )

class ImportarMaquinasForm(forms.Form):
    archivo_excel = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls',
            'help_text': 'Archivo Excel con datos de máquinas'
        })
    )
    sobrescribir = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Sobrescribir máquinas existentes con el mismo código'
    )

class ExportarMaquinasForm(forms.Form):
    FORMATO_CHOICES = [
        ('excel', 'Excel (.xlsx)'),
        ('csv', 'CSV'),
        ('pdf', 'PDF')
    ]

    formato = forms.ChoiceField(
        choices=FORMATO_CHOICES,
        initial='excel',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    incluir_inactivas = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    categorias = forms.ModelMultipleChoiceField(
        queryset=CategoriaMaquina.objects.filter(activa=True),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text='Dejar vacío para incluir todas las categorías'
    )


class ObjetoMaquinariaForm(forms.ModelForm):
    class Meta:
        model = ObjetoMaquinaria
        exclude = ['created_at', 'updated_at', 'created_by']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del objeto o pieza'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Modelo'
            }),
            'serie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de serie'
            }),
            'fabricante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del fabricante'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Rojo, Gris metalizado'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'medidas': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 30cm x 15cm x 10cm'
            }),
            'peso_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Peso en kilogramos'
            }),
            'maquina': forms.Select(attrs={
                'class': 'form-select'
            }),
            'costo': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Costo en pesos'
            }),
            'ubicacion_almacen': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Estante A3, Bodega 2'
            }),
            'fecha_compra': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_uso': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_cambio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'tiempo_uso': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 6 meses, 2 años'
            }),
            'foto_frontal': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'foto_lateral_derecha': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'foto_lateral_izquierda': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'foto_trasera': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'foto_superior': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'foto_inferior': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].required = True
        self.fields['maquina'].queryset = Maquina.objects.all().order_by('codigo_inventario')


class UsoMaquinariaForm(forms.ModelForm):
    class Meta:
        model = UsoMaquinaria
        fields = [
            'maquina', 'instructor_encargado', 'ficha',
            'fecha', 'hora_inicio', 'hora_fin',
            'horas_uso', 'horas_totales_maquina',
            'descripcion_actividad',
        ]
        widgets = {
            'maquina': forms.Select(attrs={'class': 'form-select'}),
            'instructor_encargado': forms.Select(attrs={'class': 'form-select'}),
            'ficha': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 2856721'
            }),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'hora_fin': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'horas_uso': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01', 'min': '0',
                'placeholder': '0.00'
            }),
            'horas_totales_maquina': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01', 'min': '0',
                'placeholder': '0.00'
            }),
            'descripcion_actividad': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción de la actividad realizada...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['maquina'].queryset = Maquina.objects.all().order_by('codigo_inventario')
        self.fields['maquina'].empty_label = 'Seleccione una máquina'
        self.fields['instructor_encargado'].queryset = Usuario.objects.filter(
            estado='activo'
        ).order_by('nombres')
        self.fields['instructor_encargado'].empty_label = 'Seleccione un instructor'
        self.fields['instructor_encargado'].required = False