"""
Script para crear perfil de Usuario para usuarios de Django Auth
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app_prototipo.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import Usuario, TipoUsuario

def crear_perfiles():
    """Crea perfiles de Usuario para todos los usuarios de Django Auth que no tengan uno"""
    print("=" * 60)
    print("CREACION DE PERFILES DE USUARIO")
    print("=" * 60)

    # Verificar/crear tipo de usuario por defecto
    print("\n1. Verificando tipo de usuario por defecto...")
    print("-" * 60)
    tipo_admin, created = TipoUsuario.objects.get_or_create(
        nombre='Administrador',
        defaults={
            'descripcion': 'Usuario administrador del sistema',
            'permisos': {'all': True},
            'activo': True
        }
    )
    if created:
        print(f"  [OK] Tipo de usuario 'Administrador' creado")
    else:
        print(f"  [OK] Tipo de usuario 'Administrador' ya existe")

    # Obtener todos los usuarios de Django
    django_users = User.objects.all()
    print(f"\n2. Encontrados {django_users.count()} usuarios en Django Auth")
    print("-" * 60)

    created_count = 0
    skipped_count = 0

    for user in django_users:
        print(f"\nProcesando user: {user.username}")

        # Verificar si ya tiene perfil
        if Usuario.objects.filter(numero_documento=user.username).exists():
            print(f"  [SKIP] Ya tiene perfil de Usuario")
            skipped_count += 1
            continue

        # Crear perfil de Usuario
        try:
            # Intentar extraer nombre y apellido del username si es posible
            # Por defecto usar el username como nombre
            nombres = user.first_name if user.first_name else user.username.capitalize()
            apellidos = user.last_name if user.last_name else "Usuario"

            usuario = Usuario.objects.create(
                tipo_documento='CC',
                numero_documento=user.username,  # Usar username como numero_documento
                nombres=nombres,
                apellidos=apellidos,
                email=user.email if user.email else f"{user.username}@example.com",
                telefono='',
                tipo_usuario=tipo_admin,
                centro_formacion='Centro Principal',
                especialidad='',
                cargo='Administrador' if user.is_staff else 'Usuario',
                estado='activo',
            )
            print(f"  [OK] Perfil de Usuario creado: {usuario.nombre_completo}")
            created_count += 1
        except Exception as e:
            print(f"  [ERROR] Error al crear perfil: {str(e)}")

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"Perfiles creados: {created_count}")
    print(f"Perfiles ya existentes: {skipped_count}")
    print(f"Total usuarios: {django_users.count()}")
    print("=" * 60)

    # Verificar estado final
    print("\n" + "=" * 60)
    print("ESTADO FINAL - USUARIOS CON PERFIL")
    print("=" * 60)
    for user in django_users:
        try:
            usuario = Usuario.objects.get(numero_documento=user.username)
            print(f"  [OK] {user.username} -> {usuario.nombre_completo}")
        except Usuario.DoesNotExist:
            print(f"  [ERROR] {user.username} -> NO TIENE PERFIL")
    print("=" * 60)

if __name__ == '__main__':
    crear_perfiles()
