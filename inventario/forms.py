from django import forms
from .models import PiezaInventario
from usuarios.models import Usuario


class PiezaInventarioForm(forms.ModelForm):
    class Meta:
        model  = PiezaInventario
        fields = [
            # Identificación
            'codigo_inventario', 'nombre', 'numero_serie', 'numero_factura', 'condicion',
            # Clasificación
            'categoria', 'marca', 'fabricante', 'modelo', 'color',
            # Características físicas
            'peso', 'dimensiones',
            # Ubicación y responsabilidad
            'centro_formacion', 'ambiente_formacion', 'ubicacion', 'responsable', 'proveedor',
            # Máquina asociada
            'maquina',
            # Adquisición y uso
            'valor_adquisicion', 'garantia_meses',
            'fecha_compra', 'fecha_uso', 'fecha_cambio',
            'horas_uso', 'horas_uso_maximas',
            # Fotografías generales
            'foto_pieza', 'foto_empaque',
            # Fotografías 6 ángulos
            'foto_frontal', 'foto_lateral_derecha', 'foto_lateral_izquierda',
            'foto_trasera', 'foto_superior', 'foto_inferior',
            # Detalles técnicos
            'especificaciones_tecnicas', 'observaciones',
        ]
        widgets = {
            'codigo_inventario': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ej: INV-2024-001'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nombre de la pieza u objeto'
            }),
            'numero_serie': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Número de serie'
            }),
            'numero_factura': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'N° de factura'
            }),
            'condicion': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ej: Hidráulica, Eléctrica...'
            }),
            'marca': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Marca comercial'
            }),
            'fabricante': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nombre del fabricante'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Modelo'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Color principal'
            }),
            'peso': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ej: 12.5 kg'
            }),
            'dimensiones': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ej: 30x20x15 cm'
            }),
            'centro_formacion': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Centro de formación'
            }),
            'ambiente_formacion': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ambiente de formación'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ubicación física / almacén'
            }),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'proveedor': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nombre del proveedor'
            }),
            'maquina': forms.Select(attrs={'class': 'form-select'}),
            'valor_adquisicion': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'min': '0'
            }),
            'garantia_meses': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': '0', 'min': '0'
            }),
            'fecha_compra': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'fecha_uso': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'fecha_cambio': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'horas_uso': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': '0', 'step': '0.01', 'min': '0'
            }),
            'horas_uso_maximas': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': 'Horas máximas permitidas', 'step': '0.01', 'min': '0'
            }),
            'foto_pieza': forms.ClearableFileInput(attrs={
                'class': 'form-control', 'accept': 'image/*'
            }),
            'foto_empaque': forms.ClearableFileInput(attrs={
                'class': 'form-control', 'accept': 'image/*'
            }),
            'foto_frontal': forms.ClearableFileInput(attrs={
                'class': 'form-control', 'accept': 'image/*'
            }),
            'foto_lateral_derecha': forms.ClearableFileInput(attrs={
                'class': 'form-control', 'accept': 'image/*'
            }),
            'foto_lateral_izquierda': forms.ClearableFileInput(attrs={
                'class': 'form-control', 'accept': 'image/*'
            }),
            'foto_trasera': forms.ClearableFileInput(attrs={
                'class': 'form-control', 'accept': 'image/*'
            }),
            'foto_superior': forms.ClearableFileInput(attrs={
                'class': 'form-control', 'accept': 'image/*'
            }),
            'foto_inferior': forms.ClearableFileInput(attrs={
                'class': 'form-control', 'accept': 'image/*'
            }),
            'especificaciones_tecnicas': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Especificaciones técnicas...'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['responsable'].queryset = Usuario.objects.filter(estado='activo').order_by('nombres')
        self.fields['responsable'].empty_label = 'Seleccione un responsable'
        self.fields['responsable'].required = False
        self.fields['maquina'].empty_label = 'Sin máquina asociada (opcional)'
        self.fields['maquina'].required = False
        # Fotos de ángulos no son requeridas
        for f in ['foto_frontal', 'foto_lateral_derecha', 'foto_lateral_izquierda',
                  'foto_trasera', 'foto_superior', 'foto_inferior',
                  'foto_pieza', 'foto_empaque']:
            self.fields[f].required = False
