from django import forms
from .models import Documento, TipoDocumento, CategoriaDocumento
from maquinaria.models import Maquina

class DocumentoForm(forms.ModelForm):
    palabras_clave_texto = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Palabras clave separadas por comas'
        }),
        help_text='Ingrese palabras clave separadas por comas'
    )

    class Meta:
        model = Documento
        exclude = [
            'fecha_creacion', 'fecha_modificacion', 'creado_por',
            'modificado_por', 'total_descargas', 'total_visualizaciones',
            'contenido_texto', 'indices_busqueda', 'tamaño_archivo', 'checksum',
            'palabras_clave', 'ultima_descarga'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del documento'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del documento...'
            }),
            'tipo_documento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'archivo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.txt,.xlsx,.xls,.ppt,.pptx'
            }),
            'version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 1.0, 2.1'
            }),
            'autor_original': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Autor del documento'
            }),
            'nivel_acceso': forms.Select(attrs={
                'class': 'form-select'
            }),
            'usuarios_acceso': forms.CheckboxSelectMultiple(),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_publicacion': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'maquina_relacionada': forms.Select(attrs={
                'class': 'form-select'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar tipos y categorías activos
        self.fields['tipo_documento'].queryset = TipoDocumento.objects.filter(activo=True)
        self.fields['categoria'].queryset = CategoriaDocumento.objects.filter(activo=True)
        self.fields['maquina_relacionada'].queryset = Maquina.objects.exclude(estado='retirada')
        self.fields['maquina_relacionada'].empty_label = "Sin máquina asociada"

        # Si hay una instancia, cargar palabras clave como texto
        if self.instance and self.instance.pk and self.instance.palabras_clave:
            if isinstance(self.instance.palabras_clave, list):
                self.initial['palabras_clave_texto'] = ', '.join(self.instance.palabras_clave)
            else:
                self.initial['palabras_clave_texto'] = self.instance.palabras_clave

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Procesar palabras clave
        palabras_clave_texto = self.cleaned_data.get('palabras_clave_texto', '')
        if palabras_clave_texto:
            # Convertir string separado por comas a lista
            lista_palabras = [palabra.strip() for palabra in palabras_clave_texto.split(',')]
            instance.palabras_clave = [p for p in lista_palabras if p]  # Eliminar vacíos
        else:
            instance.palabras_clave = []

        if commit:
            instance.save()
            self.save_m2m()
        return instance

class SubirDocumentoRapidoForm(forms.Form):
    """Formulario simplificado para subida rápida de documentos"""
    archivo = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx,.txt,.xlsx,.xls,.ppt,.pptx'
        })
    )
    categoria = forms.ModelChoiceField(
        queryset=CategoriaDocumento.objects.filter(activo=True),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    maquina_relacionada = forms.ModelChoiceField(
        queryset=Maquina.objects.exclude(estado='retirada'),
        required=False,
        empty_label="Sin máquina asociada",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

class TipoDocumentoForm(forms.ModelForm):
    class Meta:
        model = TipoDocumento
        fields = ['nombre', 'descripcion', 'extensiones_permitidas', 'tamaño_maximo_mb', 'icono', 'color', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del tipo de documento'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del tipo de documento...'
            }),
            'extensiones_permitidas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Ejemplo: [".pdf", ".doc", ".docx"]'
            }),
            'tamaño_maximo_mb': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '500'
            }),
            'icono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: bi-file-text, bi-file-pdf'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def clean_extensiones_permitidas(self):
        extensiones = self.cleaned_data.get('extensiones_permitidas', '')
        if extensiones:
            import json
            try:
                return json.loads(extensiones)
            except json.JSONDecodeError:
                # Si no es JSON válido, intentar como lista separada por comas
                return [ext.strip() for ext in extensiones.split(',')]
        return []

class CategoriaDocumentoForm(forms.ModelForm):
    class Meta:
        model = CategoriaDocumento
        fields = ['nombre', 'descripcion', 'parent', 'icono', 'color', 'orden', 'activo']
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
            'parent': forms.Select(attrs={
                'class': 'form-select'
            }),
            'icono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: bi-folder, bi-folder-open'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'orden': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Evitar que una categoría sea padre de sí misma
        if self.instance.pk:
            self.fields['parent'].queryset = CategoriaDocumento.objects.exclude(pk=self.instance.pk)
        self.fields['parent'].empty_label = "Sin categoría padre"

class BuscarDocumentosForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por título, contenido, palabras clave...'
        })
    )
    categoria = forms.ModelChoiceField(
        queryset=CategoriaDocumento.objects.filter(activo=True),
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    tipo_documento = forms.ModelChoiceField(
        queryset=TipoDocumento.objects.filter(activo=True),
        required=False,
        empty_label="Todos los tipos",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Documento.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    nivel_acceso = forms.ChoiceField(
        choices=[('', 'Todos los niveles')] + Documento.NIVEL_ACCESO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    maquina_relacionada = forms.ModelChoiceField(
        queryset=Maquina.objects.exclude(estado='retirada'),
        required=False,
        empty_label="Todas las máquinas",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
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

class GestionarPermisosForm(forms.Form):
    """Formulario para gestionar permisos de acceso a documentos"""
    usuarios_con_acceso = forms.ModelMultipleChoiceField(
        queryset=None,  # Se establece en __init__
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        help_text='Usuarios que tendrán acceso al documento'
    )
    nivel_acceso = forms.ChoiceField(
        choices=Documento.NIVEL_ACCESO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from usuarios.models import Usuario
        self.fields['usuarios_con_acceso'].queryset = Usuario.objects.filter(estado='activo')

class ComentarioDocumentoForm(forms.Form):
    """Formulario para agregar comentarios a documentos"""
    comentario = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Escribe tu comentario sobre este documento...'
        })
    )

class ImportarDocumentosForm(forms.Form):
    """Formulario para importación masiva de documentos"""
    archivo_zip = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.zip',
            'help_text': 'Archivo ZIP con documentos y archivo CSV de metadatos'
        })
    )
    categoria_por_defecto = forms.ModelChoiceField(
        queryset=CategoriaDocumento.objects.filter(activo=True),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text='Categoría para documentos sin categoría especificada'
    )
    sobrescribir_existentes = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Sobrescribir documentos existentes con mismo nombre'
    )

class ValidarArchivoForm(forms.Form):
    """Formulario para validar archivos antes de subir"""
    archivo = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control'
        })
    )

class ConfiguracionDocumentosForm(forms.Form):
    """Formulario para configurar sistema de documentos"""
    ruta_almacenamiento = forms.CharField(
        initial='documentos/',
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
        help_text='Ruta base para almacenar documentos'
    )
    tamaño_maximo_global_mb = forms.IntegerField(
        initial=100,
        min_value=1,
        max_value=1000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        }),
        help_text='Tamaño máximo global para documentos (MB)'
    )
    permitir_descarga_anonima = forms.BooleanField(
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Permitir descarga sin autenticación para documentos públicos'
    )
    activar_versionado = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Mantener versiones anteriores de documentos'
    )
    max_versiones_por_documento = forms.IntegerField(
        initial=10,
        min_value=1,
        max_value=50,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        }),
        help_text='Número máximo de versiones a mantener por documento'
    )
    indexar_contenido = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Extraer e indexar texto de documentos para búsqueda'
    )
    notificar_nuevos_documentos = forms.BooleanField(
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Notificar a usuarios relevantes cuando se suban nuevos documentos'
    )

class NuevaVersionForm(forms.Form):
    """Formulario para subir nueva versión de documento"""
    archivo = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control'
        })
    )
    numero_version = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 1.1, 2.0'
        })
    )
    comentarios_cambios = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Describe los cambios realizados en esta versión...'
        })
    )

class FiltroMisDocumentosForm(forms.Form):
    """Formulario para filtrar documentos del usuario"""
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Documento.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    categoria = forms.ModelChoiceField(
        queryset=CategoriaDocumento.objects.filter(activo=True),
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    ordenar_por = forms.ChoiceField(
        choices=[
            ('-fecha_modificacion', 'Más recientes'),
            ('fecha_modificacion', 'Más antiguos'),
            ('titulo', 'Título A-Z'),
            ('-titulo', 'Título Z-A'),
            ('-total_descargas', 'Más descargados')
        ],
        initial='-fecha_modificacion',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )