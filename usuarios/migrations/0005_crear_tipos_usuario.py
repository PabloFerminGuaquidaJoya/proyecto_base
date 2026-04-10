from django.db import migrations


TIPOS = [
    {
        'nombre': 'Administrador',
        'descripcion': 'Administrador del sistema — acceso total.',
        'permisos': {'all': True},
    },
    {
        'nombre': 'Instructor',
        'descripcion': 'Instructor SENA — gestión de maquinaria, documentos y reportes.',
        'permisos': {'maquinaria': True, 'documentos': True, 'reportes': True, 'backups': True},
    },
    {
        'nombre': 'Staff',
        'descripcion': 'Personal administrativo — acceso de soporte y gestión.',
        'permisos': {'maquinaria': True, 'documentos': True, 'backups': True},
    },
    {
        'nombre': 'Aprendiz',
        'descripcion': 'Aprendiz SENA — acceso de consulta.',
        'permisos': {'maquinaria': False, 'documentos': True, 'backups': False},
    },
]


def crear_tipos(apps, schema_editor):
    TipoUsuario = apps.get_model('usuarios', 'TipoUsuario')
    for datos in TIPOS:
        TipoUsuario.objects.get_or_create(
            nombre=datos['nombre'],
            defaults={
                'descripcion': datos['descripcion'],
                'permisos': datos['permisos'],
                'activo': True,
            },
        )


def revertir_tipos(apps, schema_editor):
    # No eliminamos para preservar integridad de FK existentes
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0004_usuario_ficha_alter_usuario_centro_formacion'),
    ]

    operations = [
        migrations.RunPython(crear_tipos, revertir_tipos),
    ]
