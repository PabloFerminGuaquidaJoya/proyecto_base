from django import forms
from .models import PiezaInventario
from usuarios.models import Usuario


class PiezaInventarioForm(forms.ModelForm):
    class Meta:
        model  = PiezaInventario
        fields = [
            'codigo_inventario', 'nombre', 'numero_serie', 'numero_factura',
            'categoria', 'marca', 'modelo',
            'peso', 'dimensiones',
            'centro_formacion', 'ambiente_formacion', 'ubicacion', 'responsable',
            'proveedor', 'valor_adquisicion', 'garantia_meses',
            'horas_uso', 'horas_uso_maximas',
            'condicion',
            'foto_pieza', 'foto_empaque',
            'especificaciones_tecnicas', 'observaciones',
        ]
        widgets = {
            'codigo_inventario': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ej: INV-2024-001'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nombre de la pieza'
            }),
            'numero_serie': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Número de serie'
            }),
            'numero_factura': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'N° de factura'
            }),
            'categoria': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ej: Hidráulica, Eléctrica...'
            }),
            'marca': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Marca'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Modelo'
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
                'class': 'form-control', 'placeholder': 'Ubicación física'
            }),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'proveedor': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nombre del proveedor'
            }),
            'valor_adquisicion': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'min': '0'
            }),
            'garantia_meses': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': '0', 'min': '0'
            }),
            'horas_uso': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': '0', 'step': '0.01', 'min': '0'
            }),
            'horas_uso_maximas': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': 'Horas máximas permitidas', 'step': '0.01', 'min': '0'
            }),
            'condicion': forms.Select(attrs={'class': 'form-select'}),
            'foto_pieza': forms.ClearableFileInput(attrs={
                'class': 'form-control', 'accept': 'image/*'
            }),
            'foto_empaque': forms.ClearableFileInput(attrs={
                'class': 'form-control', 'accept': 'image/*'
            }),
            'especificaciones_tecnicas': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Especificaciones técnicas de la pieza...'
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
