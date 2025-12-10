#!/usr/bin/env python
"""
Script para crear datos iniciales del sistema
"""
import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app_prototipo.settings')
django.setup()

from maquinaria.models import CategoriaMaquina, Proveedor
from usuarios.models import TipoUsuario

def crear_categorias():
    """Crear categorías de máquinas"""
    categorias = [
        {
            'nombre': 'Excavadoras',
            'descripcion': 'Máquinas para excavación y movimiento de tierras'
        },
        {
            'nombre': 'Bulldozers',
            'descripcion': 'Tractores de oruga para nivelación y empuje'
        },
        {
            'nombre': 'Grúas',
            'descripcion': 'Equipos para elevación y manejo de cargas pesadas'
        },
        {
            'nombre': 'Cargadoras',
            'descripcion': 'Máquinas para carga y transporte de materiales'
        },
        {
            'nombre': 'Compactadoras',
            'descripcion': 'Equipos para compactación de suelos y pavimentos'
        },
        {
            'nombre': 'Retroexcavadoras',
            'descripcion': 'Máquinas versátiles para excavación y carga'
        }
    ]

    print("Creando categorías de máquinas...")
    for cat_data in categorias:
        categoria, created = CategoriaMaquina.objects.get_or_create(
            nombre=cat_data['nombre'],
            defaults={'descripcion': cat_data['descripcion']}
        )
        if created:
            print(f"+ Categoría creada: {categoria.nombre}")
        else:
            print(f"- Categoría existente: {categoria.nombre}")

def crear_proveedores():
    """Crear proveedores"""
    proveedores = [
        {
            'nombre': 'Caterpillar Colombia S.A.',
            'nit': '800123456-1',
            'contacto_nombre': 'Juan Pérez',
            'contacto_telefono': '+57 1 234-5678',
            'contacto_email': 'ventas@caterpillar.com.co',
            'direccion': 'Calle 100 #25-34',
            'ciudad': 'Bogotá',
            'pais': 'Colombia',
            'sitio_web': 'https://www.caterpillar.com'
        },
        {
            'nombre': 'Komatsu Andina S.A.',
            'nit': '800234567-2',
            'contacto_nombre': 'María González',
            'contacto_telefono': '+57 1 345-6789',
            'contacto_email': 'info@komatsu.com.co',
            'direccion': 'Carrera 15 #93-47',
            'ciudad': 'Bogotá',
            'pais': 'Colombia',
            'sitio_web': 'https://www.komatsu.com'
        },
        {
            'nombre': 'John Deere Colombia',
            'nit': '800345678-3',
            'contacto_nombre': 'Carlos Rodríguez',
            'contacto_telefono': '+57 1 456-7890',
            'contacto_email': 'contacto@johndeere.com.co',
            'direccion': 'Avenida 68 #40-35',
            'ciudad': 'Bogotá',
            'pais': 'Colombia',
            'sitio_web': 'https://www.deere.com'
        },
        {
            'nombre': 'Case Construction Equipment',
            'nit': '800456789-4',
            'contacto_nombre': 'Ana Martínez',
            'contacto_telefono': '+57 1 567-8901',
            'contacto_email': 'ventas@case.com.co',
            'direccion': 'Zona Industrial Norte',
            'ciudad': 'Medellín',
            'pais': 'Colombia',
            'sitio_web': 'https://www.casece.com'
        },
        {
            'nombre': 'Volvo Construction Equipment',
            'nit': '800567890-5',
            'contacto_nombre': 'Roberto Silva',
            'contacto_telefono': '+57 1 678-9012',
            'contacto_email': 'info@volvo.com.co',
            'direccion': 'Calle 72 #10-34',
            'ciudad': 'Bogotá',
            'pais': 'Colombia',
            'sitio_web': 'https://www.volvoce.com'
        }
    ]

    print("\nCreando proveedores...")
    for prov_data in proveedores:
        proveedor, created = Proveedor.objects.get_or_create(
            nombre=prov_data['nombre'],
            defaults=prov_data
        )
        if created:
            print(f"+ Proveedor creado: {proveedor.nombre}")
        else:
            print(f"- Proveedor existente: {proveedor.nombre}")

def crear_tipos_usuario():
    """Crear tipos de usuario"""
    tipos = [
        {
            'nombre': 'Administrador',
            'descripcion': 'Acceso completo al sistema',
            'permisos': {
                'crear': True,
                'editar': True,
                'eliminar': True,
                'ver_reportes': True,
                'administrar_usuarios': True
            }
        },
        {
            'nombre': 'Instructor',
            'descripcion': 'Acceso para gestión de maquinaria en programas de formación',
            'permisos': {
                'crear': True,
                'editar': True,
                'eliminar': False,
                'ver_reportes': True,
                'administrar_usuarios': False
            }
        },
        {
            'nombre': 'Técnico',
            'descripcion': 'Acceso para mantenimiento y operación de máquinas',
            'permisos': {
                'crear': False,
                'editar': True,
                'eliminar': False,
                'ver_reportes': False,
                'administrar_usuarios': False
            }
        },
        {
            'nombre': 'Aprendiz',
            'descripcion': 'Acceso de solo lectura para consulta',
            'permisos': {
                'crear': False,
                'editar': False,
                'eliminar': False,
                'ver_reportes': False,
                'administrar_usuarios': False
            }
        }
    ]

    print("\nCreando tipos de usuario...")
    for tipo_data in tipos:
        tipo, created = TipoUsuario.objects.get_or_create(
            nombre=tipo_data['nombre'],
            defaults=tipo_data
        )
        if created:
            print(f"+ Tipo de usuario creado: {tipo.nombre}")
        else:
            print(f"- Tipo de usuario existente: {tipo.nombre}")

def main():
    print("=== Creando datos iniciales del sistema ===\n")

    crear_tipos_usuario()
    crear_categorias()
    crear_proveedores()

    print("\n=== ¡Datos iniciales creados exitosamente! ===")
    print("\nAhora puedes:")
    print("1. Acceder al admin: http://127.0.0.1:8000/admin/")
    print("2. Crear usuarios desde el admin")
    print("3. Crear máquinas desde la interfaz web")
    print("4. Gestionar todo desde el panel de administración")

if __name__ == '__main__':
    main()