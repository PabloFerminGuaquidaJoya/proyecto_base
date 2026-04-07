import re
from django.core.exceptions import ValidationError


class ComplejidadPasswordValidator:
    """
    Valida que la contraseña cumpla requisitos de complejidad:
    - Mínimo 8 caracteres
    - Al menos una mayúscula
    - Al menos una minúscula
    - Al menos un número
    - Al menos un carácter especial
    """

    def validate(self, password, user=None):
        errors = []
        if len(password) < 8:
            errors.append('Debe tener al menos 8 caracteres.')
        if not re.search(r'[A-Z]', password):
            errors.append('Debe contener al menos una letra mayúscula.')
        if not re.search(r'[a-z]', password):
            errors.append('Debe contener al menos una letra minúscula.')
        if not re.search(r'\d', password):
            errors.append('Debe contener al menos un número.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-\+\=\[\]\\\/]', password):
            errors.append('Debe contener al menos un carácter especial (!@#$%^&*...).')
        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return (
            'La contraseña debe tener mínimo 8 caracteres, '
            'una mayúscula, una minúscula, un número y un carácter especial.'
        )
