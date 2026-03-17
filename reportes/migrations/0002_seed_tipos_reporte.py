from django.db import migrations


def seed_tipos_reporte(apps, schema_editor):
    TipoReporte = apps.get_model('reportes', 'TipoReporte')
    tipos = [
        {
            'nombre': 'Reporte de Maquinaria',
            'descripcion': (
                'Información completa de la maquinaria registrada: datos generales, '
                'mantenimientos realizados y usos registrados por sesión.'
            ),
            'formato_salida': ['pdf', 'excel', 'csv', 'json'],
        },
        {
            'nombre': 'Reporte de Inventario',
            'descripcion': (
                'Listado de objetos del inventario ordenados desde los más nuevos '
                'hasta los más viejos y usados, con condición y horas de uso.'
            ),
            'formato_salida': ['pdf', 'excel', 'csv', 'json'],
        },
        {
            'nombre': 'Reporte de Documentos',
            'descripcion': (
                'Cuantificación y clasificación de documentos por Tipo, Categoría, '
                'Estado y Nivel de Acceso.'
            ),
            'formato_salida': ['pdf', 'excel', 'csv', 'json'],
        },
    ]
    for tipo in tipos:
        TipoReporte.objects.get_or_create(
            nombre=tipo['nombre'],
            defaults={
                'descripcion': tipo['descripcion'],
                'formato_salida': tipo['formato_salida'],
                'activo': True,
            }
        )


def reverse_seed(apps, schema_editor):
    TipoReporte = apps.get_model('reportes', 'TipoReporte')
    TipoReporte.objects.filter(nombre__in=[
        'Reporte de Maquinaria',
        'Reporte de Inventario',
        'Reporte de Documentos',
    ]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('reportes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_tipos_reporte, reverse_seed),
    ]
