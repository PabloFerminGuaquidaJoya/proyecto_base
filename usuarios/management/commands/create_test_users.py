from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from usuarios.models import Usuario, TipoUsuario

class Command(BaseCommand):
    help = 'Create test users for the system'

    def handle(self, *args, **options):
        # Create TipoUsuario instances first
        admin_tipo, created = TipoUsuario.objects.get_or_create(
            nombre='administrador',
            defaults={
                'descripcion': 'Administrador del sistema con acceso completo',
                'permisos': {'all': True},
                'activo': True
            }
        )

        instructor_tipo, created = TipoUsuario.objects.get_or_create(
            nombre='instructor',
            defaults={
                'descripcion': 'Instructor de maquinaria pesada',
                'permisos': {'maquinaria': True, 'reportes': True},
                'activo': True
            }
        )

        # Create test usuarios
        admin_user, created = Usuario.objects.get_or_create(
            numero_documento='12345678',
            defaults={
                'tipo_documento': 'CC',
                'nombres': 'Admin',
                'apellidos': 'Sistema',
                'email': 'admin@sena.edu.co',
                'telefono': '+57 300 123 4567',
                'tipo_usuario': admin_tipo,
                'centro_formacion': 'Centro de Gestión Industrial',
                'especialidad': 'Administración de Sistemas',
                'cargo': 'Administrador',
                'estado': 'activo'
            }
        )

        test_user, created = Usuario.objects.get_or_create(
            numero_documento='87654321',
            defaults={
                'tipo_documento': 'CC',
                'nombres': 'Carlos',
                'apellidos': 'Instructor',
                'email': 'instructor@sena.edu.co',
                'telefono': '+57 301 987 6543',
                'tipo_usuario': instructor_tipo,
                'centro_formacion': 'Centro de Gestión Industrial',
                'especialidad': 'Maquinaria Pesada',
                'cargo': 'Instructor',
                'estado': 'activo'
            }
        )

        # Create corresponding Django users
        django_admin, created = User.objects.get_or_create(
            username='12345678',
            defaults={
                'first_name': 'Admin',
                'last_name': 'Sistema',
                'email': 'admin@sena.edu.co',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            django_admin.set_password('admin123')
            django_admin.save()

        django_instructor, created = User.objects.get_or_create(
            username='87654321',
            defaults={
                'first_name': 'Carlos',
                'last_name': 'Instructor',
                'email': 'instructor@sena.edu.co',
                'is_active': True,
                'is_staff': False
            }
        )
        if created:
            django_instructor.set_password('instructor123')
            django_instructor.save()

        self.stdout.write(
            self.style.SUCCESS('Test users created successfully!')
        )
        self.stdout.write('Admin user: 12345678 / admin123')
        self.stdout.write('Instructor user: 87654321 / instructor123')