"""
Script para crear categorías y tipos de documentos
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app_prototipo.settings')
django.setup()

from documentos.models import TipoDocumento, CategoriaDocumento

def crear_tipos_documento():
    """Crear tipos de documento predefinidos"""
    print("\n" + "=" * 60)
    print("CREANDO TIPOS DE DOCUMENTO")
    print("=" * 60)

    tipos = [
        {
            'nombre': 'Manual de Operacion',
            'descripcion': 'Manuales de operacion y uso de maquinaria',
            'extensiones_permitidas': ['.pdf', '.doc', '.docx'],
            'tamaño_maximo_mb': 50,
            'icono': 'bi-book',
            'color': '#007bff',
        },
        {
            'nombre': 'Manual de Mantenimiento',
            'descripcion': 'Manuales de mantenimiento preventivo y correctivo',
            'extensiones_permitidas': ['.pdf', '.doc', '.docx'],
            'tamaño_maximo_mb': 50,
            'icono': 'bi-tools',
            'color': '#28a745',
        },
        {
            'nombre': 'Ficha Tecnica',
            'descripcion': 'Fichas tecnicas y especificaciones',
            'extensiones_permitidas': ['.pdf', '.doc', '.docx', '.xlsx'],
            'tamaño_maximo_mb': 25,
            'icono': 'bi-file-earmark-text',
            'color': '#17a2b8',
        },
        {
            'nombre': 'Planos',
            'descripcion': 'Planos tecnicos y diagramas',
            'extensiones_permitidas': ['.pdf', '.dwg', '.dxf'],
            'tamaño_maximo_mb': 100,
            'icono': 'bi-diagram-3',
            'color': '#ffc107',
        },
        {
            'nombre': 'Certificado',
            'descripcion': 'Certificados de calibracion, calidad, etc.',
            'extensiones_permitidas': ['.pdf'],
            'tamaño_maximo_mb': 10,
            'icono': 'bi-award',
            'color': '#fd7e14',
        },
        {
            'nombre': 'Procedimiento',
            'descripcion': 'Procedimientos operativos estandar',
            'extensiones_permitidas': ['.pdf', '.doc', '.docx'],
            'tamaño_maximo_mb': 25,
            'icono': 'bi-list-check',
            'color': '#6610f2',
        },
        {
            'nombre': 'Reporte',
            'descripcion': 'Reportes de inspeccion, auditoria, etc.',
            'extensiones_permitidas': ['.pdf', '.doc', '.docx', '.xlsx'],
            'tamaño_maximo_mb': 30,
            'icono': 'bi-file-earmark-bar-graph',
            'color': '#e83e8c',
        },
        {
            'nombre': 'Otro',
            'descripcion': 'Otros documentos',
            'extensiones_permitidas': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.ppt', '.pptx'],
            'tamaño_maximo_mb': 50,
            'icono': 'bi-file-earmark',
            'color': '#6c757d',
        },
    ]

    created_count = 0
    updated_count = 0

    for tipo_data in tipos:
        tipo, created = TipoDocumento.objects.update_or_create(
            nombre=tipo_data['nombre'],
            defaults=tipo_data
        )
        if created:
            print(f"  [CREADO] {tipo.nombre}")
            created_count += 1
        else:
            print(f"  [ACTUALIZADO] {tipo.nombre}")
            updated_count += 1

    print("\n" + "-" * 60)
    print(f"Tipos creados: {created_count}")
    print(f"Tipos actualizados: {updated_count}")
    print(f"Total tipos: {TipoDocumento.objects.count()}")
    print("=" * 60)

def crear_categorias_documento():
    """Crear categorias de documento predefinidas"""
    print("\n" + "=" * 60)
    print("CREANDO CATEGORIAS DE DOCUMENTO")
    print("=" * 60)

    categorias = [
        {
            'nombre': 'Maquinaria',
            'descripcion': 'Documentos relacionados con maquinaria',
            'icono': 'bi-gear-fill',
            'color': '#007bff',
            'orden': 1,
        },
        {
            'nombre': 'Seguridad',
            'descripcion': 'Documentos de seguridad industrial',
            'icono': 'bi-shield-check',
            'color': '#28a745',
            'orden': 2,
        },
        {
            'nombre': 'Calidad',
            'descripcion': 'Documentos de control de calidad',
            'icono': 'bi-clipboard-check',
            'color': '#17a2b8',
            'orden': 3,
        },
        {
            'nombre': 'Mantenimiento',
            'descripcion': 'Documentos de mantenimiento',
            'icono': 'bi-tools',
            'color': '#ffc107',
            'orden': 4,
        },
        {
            'nombre': 'Operacion',
            'descripcion': 'Documentos de operacion',
            'icono': 'bi-play-circle',
            'color': '#fd7e14',
            'orden': 5,
        },
        {
            'nombre': 'Tecnica',
            'descripcion': 'Documentos tecnicos generales',
            'icono': 'bi-file-earmark-code',
            'color': '#6610f2',
            'orden': 6,
        },
        {
            'nombre': 'Administrativa',
            'descripcion': 'Documentos administrativos',
            'icono': 'bi-briefcase',
            'color': '#e83e8c',
            'orden': 7,
        },
        {
            'nombre': 'General',
            'descripcion': 'Documentos generales',
            'icono': 'bi-folder',
            'color': '#6c757d',
            'orden': 8,
        },
    ]

    created_count = 0
    updated_count = 0

    for cat_data in categorias:
        categoria, created = CategoriaDocumento.objects.update_or_create(
            nombre=cat_data['nombre'],
            defaults=cat_data
        )
        if created:
            print(f"  [CREADO] {categoria.nombre}")
            created_count += 1
        else:
            print(f"  [ACTUALIZADO] {categoria.nombre}")
            updated_count += 1

    print("\n" + "-" * 60)
    print(f"Categorias creadas: {created_count}")
    print(f"Categorias actualizadas: {updated_count}")
    print(f"Total categorias: {CategoriaDocumento.objects.count()}")
    print("=" * 60)

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("POBLANDO BASE DE DATOS - MODULO DOCUMENTOS")
    print("=" * 60)

    crear_tipos_documento()
    crear_categorias_documento()

    print("\n" + "=" * 60)
    print("PROCESO COMPLETADO")
    print("=" * 60)
    print("\nLa base de datos ha sido poblada correctamente.")
    print(f"Tipos de documento: {TipoDocumento.objects.count()}")
    print(f"Categorias de documento: {CategoriaDocumento.objects.count()}")
    print("=" * 60 + "\n")
