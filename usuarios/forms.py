from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.contrib.auth.password_validation import validate_password
from .models import Usuario, TipoUsuario, SesionUsuario
from .validators import ComplejidadPasswordValidator

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Número de documento o email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Contraseña'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Usuario'
        self.fields['password'].label = 'Contraseña'

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        }),
        required=False,
        help_text='Dejar vacío para mantener la contraseña actual'
    )
    confirmar_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        }),
        required=False
    )

    class Meta:
        model = Usuario
        exclude = ['fecha_registro', 'fecha_aprobacion', 'ultimo_acceso', 'created_at', 'updated_at', 'created_by']
        widgets = {
            'tipo_documento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de documento'
            }),
            'nombres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombres completos'
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellidos completos'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+57 300 123 4567'
            }),
            'foto_perfil': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'tipo_usuario': forms.Select(attrs={
                'class': 'form-select'
            }),
            'centro_formacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Centro de formación SENA'
            }),
            'especialidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Especialidad o programa'
            }),
            'cargo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cargo o rol'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notificaciones_email': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tema_oscuro': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'idioma': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('es', 'Español'),
                ('en', 'English')
            ])
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar tipos de usuario activos
        self.fields['tipo_usuario'].queryset = TipoUsuario.objects.filter(activo=True)

        # Hacer campos requeridos
        self.fields['nombres'].required = True
        self.fields['apellidos'].required = True
        self.fields['email'].required = True
        self.fields['numero_documento'].required = True
        self.fields['tipo_usuario'].required = True

    def clean_numero_documento(self):
        numero_documento = self.cleaned_data.get('numero_documento')
        if numero_documento:
            # Validar que solo contenga números
            if not numero_documento.isdigit():
                raise forms.ValidationError('El número de documento debe contener solo números.')

            # Verificar unicidad
            if self.instance.pk:
                # Estamos editando
                if Usuario.objects.exclude(pk=self.instance.pk).filter(numero_documento=numero_documento).exists():
                    raise forms.ValidationError('Ya existe un usuario con este número de documento.')
            else:
                # Estamos creando
                if Usuario.objects.filter(numero_documento=numero_documento).exists():
                    raise forms.ValidationError('Ya existe un usuario con este número de documento.')

        return numero_documento

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Verificar unicidad del email
            if self.instance.pk:
                if Usuario.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
                    raise forms.ValidationError('Ya existe un usuario con este email.')
            else:
                if Usuario.objects.filter(email=email).exists():
                    raise forms.ValidationError('Ya existe un usuario con este email.')

        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmar_password = cleaned_data.get('confirmar_password')

        if password or confirmar_password:
            if password != confirmar_password:
                raise forms.ValidationError('Las contraseñas no coinciden.')

            if len(password) < 6:
                raise forms.ValidationError('La contraseña debe tener al menos 6 caracteres.')

        return cleaned_data

class RegistroUsuarioForm(forms.ModelForm):
    centro_formacion = forms.ChoiceField(
        choices=[('Centro Minero', 'Centro Minero')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Centro de formación'
    )
    especialidad = forms.ChoiceField(
        choices=[
            ('', 'Seleccione una especialidad'),
            ('Técnico en Operación de Maquinaria Pesada', 'Técnico en Operación de Maquinaria Pesada'),
            ('Curso complementario en Sistemas Hidráulicos en Maquinaria Pesada', 'Curso complementario en Sistemas Hidráulicos en Maquinaria Pesada'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Especialidad'
    )
    cargo = forms.ChoiceField(
        choices=[
            ('', 'Seleccione un cargo'),
            ('Aprendiz', 'Aprendiz'),
            ('Instructor', 'Instructor'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Cargo'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres, mayúscula, número y símbolo',
            'id': 'id_password',
        }),
        min_length=8,
        label='Contraseña',
        help_text='Mínimo 8 caracteres, una mayúscula, una minúscula, un número y un carácter especial.'
    )
    confirmar_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repite la contraseña',
            'id': 'id_confirmar_password',
        }),
        label='Confirmar contraseña'
    )

    class Meta:
        model = Usuario
        fields = [
            'tipo_documento', 'numero_documento', 'nombres', 'apellidos',
            'email', 'telefono', 'centro_formacion', 'especialidad', 'cargo'
        ]
        widgets = {
            'tipo_documento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de documento'
            }),
            'nombres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombres completos'
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellidos completos'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+57 300 123 4567'
            }),
        }

    def clean_numero_documento(self):
        numero_documento = self.cleaned_data.get('numero_documento')
        if numero_documento:
            # Validar que solo contenga números
            if not numero_documento.isdigit():
                raise forms.ValidationError('El número de documento debe contener solo números.')

            # Verificar unicidad
            if Usuario.objects.filter(numero_documento=numero_documento).exists():
                raise forms.ValidationError('Ya existe un usuario con este número de documento.')

        return numero_documento

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Verificar unicidad del email
            if Usuario.objects.filter(email=email).exists():
                raise forms.ValidationError('Ya existe un usuario con este email.')

        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            validator = ComplejidadPasswordValidator()
            validator.validate(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmar_password = cleaned_data.get('confirmar_password')

        if password and confirmar_password and password != confirmar_password:
            raise forms.ValidationError('Las contraseñas no coinciden.')

        return cleaned_data

class TipoUsuarioForm(forms.ModelForm):
    class Meta:
        model = TipoUsuario
        fields = ['nombre', 'descripcion', 'permisos', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del tipo de usuario'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del tipo de usuario...'
            }),
            'permisos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'JSON con permisos específicos'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'nombres', 'apellidos', 'email', 'telefono', 'foto_perfil',
            'centro_formacion', 'especialidad', 'cargo',
        ]
        widgets = {
            'nombres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombres completos'
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellidos completos'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+57 300 123 4567'
            }),
            'foto_perfil': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'centro_formacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Centro de formación SENA'
            }),
            'especialidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Especialidad o programa'
            }),
            'cargo': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('', 'Seleccione un cargo'),
                ('Aprendiz', 'Aprendiz'),
                ('Instructor', 'Instructor'),
            ]),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Verificar unicidad del email
            if self.instance.pk:
                if Usuario.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
                    raise forms.ValidationError('Ya existe un usuario con este email.')
        return email

class CambiarPasswordForm(forms.Form):
    password_actual = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña actual'
        })
    )
    password_nueva = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña (mínimo 6 caracteres)'
        }),
        min_length=6
    )
    confirmar_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password_actual(self):
        password_actual = self.cleaned_data.get('password_actual')
        if not self.user.check_password(password_actual):
            raise forms.ValidationError('La contraseña actual es incorrecta.')
        return password_actual

    def clean(self):
        cleaned_data = super().clean()
        password_nueva = cleaned_data.get('password_nueva')
        confirmar_password = cleaned_data.get('confirmar_password')

        if password_nueva != confirmar_password:
            raise forms.ValidationError('Las nuevas contraseñas no coinciden.')

        return cleaned_data

class BuscarUsuariosForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por documento, nombre, email...'
        })
    )
    tipo_usuario = forms.ModelChoiceField(
        queryset=TipoUsuario.objects.filter(activo=True),
        required=False,
        empty_label="Todos los tipos",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Usuario.ESTADO_CHOICES,
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

class ConfiguracionUsuarioForm(forms.Form):
    """Formulario para configuraciones generales del sistema de usuarios"""
    max_intentos_login = forms.IntegerField(
        min_value=3,
        max_value=10,
        initial=5,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        }),
        help_text='Número máximo de intentos de login antes de bloquear cuenta'
    )
    duracion_sesion_horas = forms.IntegerField(
        min_value=1,
        max_value=48,
        initial=8,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        }),
        help_text='Duración máxima de sesión en horas'
    )
    requerir_cambio_password_dias = forms.IntegerField(
        min_value=30,
        max_value=365,
        initial=90,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        }),
        help_text='Días antes de requerir cambio de contraseña'
    )
    permitir_registro_publico = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Permitir que usuarios se registren sin aprobación de admin'
    )

class RecuperarPasswordForm(forms.Form):
    """Formulario para solicitar recuperación de contraseña"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'correo@ejemplo.com',
            'autofocus': True
        }),
        label='Correo electrónico',
        help_text='Ingresa el correo asociado a tu cuenta'
    )

class ResetPasswordForm(forms.Form):
    """Formulario para restablecer contraseña con token"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Nueva contraseña'
        }),
        min_length=6,
        label='Nueva contraseña'
    )
    confirmar_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirmar contraseña'
        }),
        label='Confirmar contraseña'
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmar_password = cleaned_data.get('confirmar_password')

        if password and confirmar_password:
            if password != confirmar_password:
                raise forms.ValidationError('Las contraseñas no coinciden.')

        return cleaned_data