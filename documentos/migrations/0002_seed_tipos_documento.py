from django.db import migrations


TIPOS_DOCUMENTO = [
    {
        'nombre': 'Manual de Operacion',
        'descripcion': 'Manuales que describen el uso y operacion de maquinaria y equipos.',
        'extensiones_permitidas': ['.pdf', '.doc', '.docx'],
        'tamaño_maximo_mb': 50,
        'icono': 'bi-book',
        'color': '#0d6efd',
        'activo': True,
    },
    {
        'nombre': 'Manual de Mantenimiento',
        'descripcion': 'Manuales que describen procedimientos de mantenimiento preventivo y correctivo.',
        'extensiones_permitidas': ['.pdf', '.doc', '.docx'],
        'tamaño_maximo_mb': 50,
        'icono': 'bi-tools',
        'color': '#198754',
        'activo': True,
    },
    {
        'nombre': 'Documentos Tecnicos',
        'descripcion': 'Documentacion tecnica, fichas tecnicas, planos y especificaciones.',
        'extensiones_permitidas': ['.pdf', '.doc', '.docx', '.xlsx', '.xls'],
        'tamaño_maximo_mb': 100,
        'icono': 'bi-file-earmark-text',
        'color': '#0dcaf0',
        'activo': True,
    },
    {
        'nombre': 'Procedimientos',
        'descripcion': 'Procedimientos operativos estandar y protocolos de seguridad.',
        'extensiones_permitidas': ['.pdf', '.doc', '.docx', '.txt'],
        'tamaño_maximo_mb': 50,
        'icono': 'bi-list-check',
        'color': '#ffc107',
        'activo': True,
    },
]


def crear_tipos(apps, schema_editor):
    TipoDocumento = apps.get_model('documentos', 'TipoDocumento')
    for datos in TIPOS_DOCUMENTO:
        TipoDocumento.objects.get_or_create(
            nombre=datos['nombre'],
            defaults=datos,
        )


def eliminar_tipos(apps, schema_editor):
    TipoDocumento = apps.get_model('documentos', 'TipoDocumento')
    nombres = [t['nombre'] for t in TIPOS_DOCUMENTO]
    TipoDocumento.objects.filter(nombre__in=nombres).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('documentos', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(crear_tipos, eliminar_tipos),
    ]
