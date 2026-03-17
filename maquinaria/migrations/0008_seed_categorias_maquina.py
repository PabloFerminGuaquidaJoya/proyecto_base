from django.db import migrations


CATEGORIAS = [
    {
        'nombre': 'Maquinaria de Excavación y Movimiento de Tierras',
        'descripcion': 'Maquinaria para excavación, demolición y movimiento de tierras.',
        'icono': 'bi-truck',
        'color': '#dc3545',
        'activa': True,
    },
    {
        'nombre': 'Maquinaria de Carga y Transporte',
        'descripcion': 'Maquinaria para carga, descarga y transporte de materiales.',
        'icono': 'bi-truck-flatbed',
        'color': '#fd7e14',
        'activa': True,
    },
    {
        'nombre': 'Maquinaria de Nivelación y Compactación',
        'descripcion': 'Maquinaria para nivelar terrenos y compactar suelos.',
        'icono': 'bi-layers',
        'color': '#ffc107',
        'activa': True,
    },
    {
        'nombre': 'Maquinaria de Perforación',
        'descripcion': 'Maquinaria para perforación de suelos y estructuras.',
        'icono': 'bi-gear',
        'color': '#198754',
        'activa': True,
    },
    {
        'nombre': 'Maquinaria de Elevación y Izaje',
        'descripcion': 'Maquinaria para elevación, izaje y trabajos en altura.',
        'icono': 'bi-arrow-up-circle',
        'color': '#0d6efd',
        'activa': True,
    },
]


def seed_categorias(apps, schema_editor):
    CategoriaMaquina = apps.get_model('maquinaria', 'CategoriaMaquina')
    for datos in CATEGORIAS:
        CategoriaMaquina.objects.get_or_create(
            nombre=datos['nombre'],
            defaults=datos,
        )


def reverse_seed(apps, schema_editor):
    CategoriaMaquina = apps.get_model('maquinaria', 'CategoriaMaquina')
    nombres = [c['nombre'] for c in CATEGORIAS]
    CategoriaMaquina.objects.filter(nombre__in=nombres).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('maquinaria', '0007_usomaquinaria'),
    ]

    operations = [
        migrations.RunPython(seed_categorias, reverse_seed),
    ]
