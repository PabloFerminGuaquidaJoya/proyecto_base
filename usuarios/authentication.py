from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Usuario

class UsuarioBackend(BaseBackend):
    """
    Custom authentication backend for SENA users
    Allows authentication with numero_documento or email
    """

    # Roles que obtienen is_staff=True en Django
    ROLES_STAFF = ('administrador', 'staff')

    def _calcular_is_staff(self, usuario):
        """Devuelve True si el tipo_usuario del usuario tiene permisos de staff."""
        if not usuario.tipo_usuario:
            return False
        nombre = (usuario.tipo_usuario.nombre or '').lower()
        return any(r in nombre for r in self.ROLES_STAFF)

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to find user by numero_documento first
            usuario = Usuario.objects.select_related('tipo_usuario').get(
                numero_documento=username
            )
            is_staff = self._calcular_is_staff(usuario)

            # Try to get or create Django user
            django_user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': usuario.nombres,
                    'last_name': usuario.apellidos,
                    'email': usuario.email,
                    'is_active': usuario.estado == 'activo',
                    'is_staff': is_staff,
                }
            )

            # If user was just created, set password
            if created:
                django_user.set_password(password)
                django_user.save()
            else:
                # Actualizar is_staff en cada login por si cambió el rol
                if django_user.is_staff != is_staff:
                    django_user.is_staff = is_staff
                    django_user.save(update_fields=['is_staff'])

            # Check password
            if django_user.check_password(password) and django_user.is_active:
                return django_user

        except Usuario.DoesNotExist:
            # Try to authenticate by email
            try:
                usuario = Usuario.objects.select_related('tipo_usuario').get(
                    email=username
                )
                is_staff = self._calcular_is_staff(usuario)

                django_user, created = User.objects.get_or_create(
                    username=usuario.numero_documento,
                    defaults={
                        'first_name': usuario.nombres,
                        'last_name': usuario.apellidos,
                        'email': usuario.email,
                        'is_active': usuario.estado == 'activo',
                        'is_staff': is_staff,
                    }
                )

                if created:
                    django_user.set_password(password)
                    django_user.save()
                else:
                    if django_user.is_staff != is_staff:
                        django_user.is_staff = is_staff
                        django_user.save(update_fields=['is_staff'])

                if django_user.check_password(password) and django_user.is_active:
                    return django_user

            except Usuario.DoesNotExist:
                pass

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None