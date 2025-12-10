from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Usuario

class UsuarioBackend(BaseBackend):
    """
    Custom authentication backend for SENA users
    Allows authentication with numero_documento or email
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to find user by numero_documento first
            usuario = Usuario.objects.get(numero_documento=username)

            # Try to get or create Django user
            django_user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': usuario.nombres,
                    'last_name': usuario.apellidos,
                    'email': usuario.email,
                    'is_active': usuario.estado == 'activo',
                    'is_staff': usuario.tipo_usuario.nombre in ['administrador', 'coordinador'] if usuario.tipo_usuario else False
                }
            )

            # If user was just created, set password
            if created:
                django_user.set_password(password)
                django_user.save()

            # Check password
            if django_user.check_password(password) and django_user.is_active:
                return django_user

        except Usuario.DoesNotExist:
            # Try to authenticate by email
            try:
                usuario = Usuario.objects.get(email=username)
                django_user, created = User.objects.get_or_create(
                    username=usuario.numero_documento,
                    defaults={
                        'first_name': usuario.nombres,
                        'last_name': usuario.apellidos,
                        'email': usuario.email,
                        'is_active': usuario.estado == 'activo',
                        'is_staff': usuario.tipo_usuario.nombre in ['administrador', 'coordinador'] if usuario.tipo_usuario else False
                    }
                )

                if created:
                    django_user.set_password(password)
                    django_user.save()

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