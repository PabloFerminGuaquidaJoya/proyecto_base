from django.db import migrations


CATEGORIAS_DOCUMENTO = [
    {
        'nombre': 'Maquinaria de Excavación y Movimiento de Tierras',
        'descripcion': 'Documentos relacionados con maquinaria para excavación, demolición y movimiento de tierras.',
        'icono': 'bi-truck',
        'color': '#dc3545',
        'orden': 1,
        'activo': True,
    },
    {
        'nombre': 'Maquinaria de Carga y Transporte',
        'descripcion': 'Documentos relacionados con maquinaria para carga, descarga y transporte de materiales.',
        'icono': 'bi-truck-flatbed',
        'color': '#fd7e14',
        'orden': 2,
        'activo': True,
    },
    {
        'nombre': 'Maquinaria de Nivelación y Compactación',
        'descripcion': 'Documentos relacionados con maquinaria para nivelar terrenos y compactar suelos.',
        'icono': 'bi-layers',
        'color': '#ffc107',
        'orden': 3,
        'activo': True,
    },
    {
        'nombre': 'Maquinaria de Perforación',
        'descripcion': 'Documentos relacionados con maquinaria para perforación de suelos y estructuras.',
        'icono': 'bi-gear',
        'color': '#198754',
        'orden': 4,
        'activo': True,
    },
    {
        'nombre': 'Maquinaria de Elevación y Izaje',
        'descripcion': 'Documentos relacionados con maquinaria para elevación, izaje y trabajos en altura.',
        'icono': 'bi-arrow-up-circle',
        'color': '#0d6efd',
        'orden': 5,
        'activo': True,
    },
]


def crear_categorias(apps, schema_editor):
    CategoriaDocumento = apps.get_model('documentos', 'CategoriaDocumento')
    for datos in CATEGORIAS_DOCUMENTO:
        CategoriaDocumento.objects.get_or_create(
            nombre=datos['nombre'],
            defaults=datos,
        )


def eliminar_categorias(apps, schema_editor):
    CategoriaDocumento = apps.get_model('documentos', 'CategoriaDocumento')
    nombres = [c['nombre'] for c in CATEGORIAS_DOCUMENTO]
    CategoriaDocumento.objects.filter(nombre__in=nombres).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('documentos', '0002_seed_tipos_documento'),
    ]

    operations = [
        migrations.RunPython(crear_categorias, eliminar_categorias),
    ]
