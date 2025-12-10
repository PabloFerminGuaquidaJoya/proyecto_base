#!/usr/bin/env python
"""
Script para crear datos iniciales del módulo de documentos
Ejecutar: python crear_datos_documentos.py
"""
import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app_prototipo.settings')
django.setup()

from documentos.models import TipoDocumento, CategoriaDocumento

print("========================================")
print("  CREANDO DATOS INICIALES - DOCUMENTOS")
print("========================================")
print()

# Crear tipos de documento
print("[1/2] Creando tipos de documento...")

tipos = [
    {
        'nombre': 'Manual de Operación',
        'descripcion': 'Manuales de operación y uso de maquinaria',
        'extensiones_permitidas': ['.pdf', '.doc', '.docx'],
        'tamaño_maximo_mb': 50,
        'icono': 'bi-file-text',
        'color': '#007bff'
    },
    {
        'nombre': 'Manual de Mantenimiento',
        'descripcion': 'Manuales de mantenimiento preventivo y correctivo',
        'extensiones_permitidas': ['.pdf', '.doc', '.docx'],
        'tamaño_maximo_mb': 50,
        'icono': 'bi-wrench',
        'color': '#28a745'
    },
    {
        'nombre': 'Ficha Técnica',
        'descripcion': 'Fichas técnicas y especificaciones',
        'extensiones_permitidas': ['.pdf', '.doc', '.docx', '.xlsx'],
        'tamaño_maximo_mb': 25,
        'icono': 'bi-file-earmark-spreadsheet',
        'color': '#17a2b8'
    },
    {
        'nombre': 'Procedimiento',
        'descripcion': 'Procedimientos operativos estándar',
        'extensiones_permitidas': ['.pdf', '.doc', '.docx'],
        'tamaño_maximo_mb': 30,
        'icono': 'bi-list-check',
        'color': '#ffc107'
    },
    {
        'nombre': 'Certificado',
        'descripcion': 'Certificados y documentos de calibración',
        'extensiones_permitidas': ['.pdf'],
        'tamaño_maximo_mb': 10,
        'icono': 'bi-award',
        'color': '#dc3545'
    },
]

for tipo_data in tipos:
    tipo, created = TipoDocumento.objects.get_or_create(
        nombre=tipo_data['nombre'],
        defaults=tipo_data
    )
    if created:
        print(f"   ✓ Creado: {tipo.nombre}")
    else:
        print(f"   - Ya existe: {tipo.nombre}")

print()

# Crear categorías de documento
print("[2/2] Creando categorías de documento...")

categorias = [
    {
        'nombre': 'Maquinaria Pesada',
        'descripcion': 'Documentos relacionados con maquinaria pesada',
        'icono': 'bi-truck',
        'color': '#343a40',
        'orden': 1
    },
    {
        'nombre': 'Herramientas Eléctricas',
        'descripcion': 'Documentos de herramientas eléctricas',
        'icono': 'bi-lightning',
        'color': '#ffc107',
        'orden': 2
    },
    {
        'nombre': 'Equipos de Medición',
        'descripcion': 'Documentos de equipos de medición y calibración',
        'icono': 'bi-speedometer',
        'color': '#17a2b8',
        'orden': 3
    },
    {
        'nombre': 'Seguridad Industrial',
        'descripcion': 'Documentos de seguridad y protección',
        'icono': 'bi-shield-check',
        'color': '#28a745',
        'orden': 4
    },
    {
        'nombre': 'Sistemas Hidráulicos',
        'descripcion': 'Documentos de sistemas hidráulicos',
        'icono': 'bi-droplet',
        'color': '#007bff',
        'orden': 5
    },
    {
        'nombre': 'Sistemas Eléctricos',
        'descripcion': 'Documentos de sistemas eléctricos',
        'icono': 'bi-plug',
        'color': '#6f42c1',
        'orden': 6
    },
    {
        'nombre': 'Documentos Generales',
        'descripcion': 'Otros documentos técnicos',
        'icono': 'bi-folder',
        'color': '#6c757d',
        'orden': 10
    },
]

for cat_data in categorias:
    categoria, created = CategoriaDocumento.objects.get_or_create(
        nombre=cat_data['nombre'],
        defaults=cat_data
    )
    if created:
        print(f"   ✓ Creada: {categoria.nombre}")
    else:
        print(f"   - Ya existe: {categoria.nombre}")

print()
print("========================================")
print("  DATOS INICIALES CREADOS EXITOSAMENTE")
print("========================================")
print()
print(f"Total tipos de documento: {TipoDocumento.objects.count()}")
print(f"Total categorías: {CategoriaDocumento.objects.count()}")
print()
