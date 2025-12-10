"""
Script para verificar usuarios en la base de datos
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app_prototipo.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import Usuario

def verificar_usuarios():
    """Verifica los usuarios en el sistema"""
    print("=" * 60)
    print("VERIFICACION DE USUARIOS EN EL SISTEMA")
    print("=" * 60)

    # Verificar usuarios de Django Auth
    print("\n1. Usuarios en django.contrib.auth.models.User:")
    print("-" * 60)
    django_users = User.objects.all()
    if django_users.exists():
        for user in django_users:
            print(f"  - Username: {user.username}")
            print(f"    Email: {user.email}")
            print(f"    Staff: {user.is_staff}")
            print(f"    Activo: {user.is_active}")
            print()
    else:
        print("  [ADVERTENCIA] No hay usuarios en User")

    # Verificar usuarios personalizados
    print("\n2. Usuarios en usuarios.models.Usuario:")
    print("-" * 60)
    custom_users = Usuario.objects.all()
    if custom_users.exists():
        for usuario in custom_users:
            print(f"  - Nombre: {usuario.nombre_completo}")
            print(f"    Numero Documento: {usuario.numero_documento}")
            print(f"    Email: {usuario.email}")
            print(f"    Estado: {usuario.estado}")
            print()
    else:
        print("  [ADVERTENCIA] No hay usuarios en Usuario")

    # Verificar coincidencias
    print("\n3. Verificacion de coincidencias:")
    print("-" * 60)
    if django_users.exists():
        for user in django_users:
            try:
                usuario = Usuario.objects.get(numero_documento=user.username)
                print(f"  [OK] User '{user.username}' tiene perfil de Usuario: {usuario.nombre_completo}")
            except Usuario.DoesNotExist:
                print(f"  [ERROR] User '{user.username}' NO tiene perfil de Usuario")
                print(f"         Necesitas crear un Usuario con numero_documento='{user.username}'")

    print("\n" + "=" * 60)
    print(f"Total Users (Django): {django_users.count()}")
    print(f"Total Usuarios (Custom): {custom_users.count()}")
    print("=" * 60)

if __name__ == '__main__':
    verificar_usuarios()
