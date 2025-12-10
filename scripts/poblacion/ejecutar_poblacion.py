import sqlite3
import json
from datetime import datetime

# Conectar a la base de datos
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("=" * 60)
print("INSERTANDO TIPOS DE DOCUMENTO")
print("=" * 60)

# Tipos de documento
tipos = [
    ('Manual de Operacion', 'Manuales de operacion y uso de maquinaria', '[".pdf", ".doc", ".docx"]', 50, 'bi-book', '#007bff'),
    ('Manual de Mantenimiento', 'Manuales de mantenimiento preventivo y correctivo', '[".pdf", ".doc", ".docx"]', 50, 'bi-tools', '#28a745'),
    ('Ficha Tecnica', 'Fichas tecnicas y especificaciones', '[".pdf", ".doc", ".docx", ".xlsx"]', 25, 'bi-file-earmark-text', '#17a2b8'),
    ('Planos', 'Planos tecnicos y diagramas', '[".pdf", ".dwg", ".dxf"]', 100, 'bi-diagram-3', '#ffc107'),
    ('Certificado', 'Certificados de calibracion, calidad, etc.', '[".pdf"]', 10, 'bi-award', '#fd7e14'),
    ('Procedimiento', 'Procedimientos operativos estandar', '[".pdf", ".doc", ".docx"]', 25, 'bi-list-check', '#6610f2'),
    ('Reporte', 'Reportes de inspeccion, auditoria, etc.', '[".pdf", ".doc", ".docx", ".xlsx"]', 30, 'bi-file-earmark-bar-graph', '#e83e8c'),
    ('Otro', 'Otros documentos', '[".pdf", ".doc", ".docx", ".txt", ".xlsx", ".ppt", ".pptx"]', 50, 'bi-file-earmark', '#6c757d'),
]

tipos_insertados = 0
for nombre, desc, ext, tam, icono, color in tipos:
    try:
        cursor.execute("""
            INSERT INTO documentos_tipodocumento
            (nombre, descripcion, extensiones_permitidas, tamaño_maximo_mb, icono, color, activo, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, datetime('now'), datetime('now'))
        """, (nombre, desc, ext, tam, icono, color))
        print(f"  [OK] Insertado: {nombre}")
        tipos_insertados += 1
    except sqlite3.IntegrityError:
        print(f"  [SKIP] Ya existe: {nombre}")

conn.commit()
print(f"\nTipos insertados: {tipos_insertados}")

print("\n" + "=" * 60)
print("INSERTANDO CATEGORIAS DE DOCUMENTO")
print("=" * 60)

# Categorías de documento
categorias = [
    ('Maquinaria', 'Documentos relacionados con maquinaria', 'bi-gear-fill', '#007bff', 1),
    ('Seguridad', 'Documentos de seguridad industrial', 'bi-shield-check', '#28a745', 2),
    ('Calidad', 'Documentos de control de calidad', 'bi-clipboard-check', '#17a2b8', 3),
    ('Mantenimiento', 'Documentos de mantenimiento', 'bi-tools', '#ffc107', 4),
    ('Operacion', 'Documentos de operacion', 'bi-play-circle', '#fd7e14', 5),
    ('Tecnica', 'Documentos tecnicos generales', 'bi-file-earmark-code', '#6610f2', 6),
    ('Administrativa', 'Documentos administrativos', 'bi-briefcase', '#e83e8c', 7),
    ('General', 'Documentos generales', 'bi-folder', '#6c757d', 8),
]

categorias_insertadas = 0
for nombre, desc, icono, color, orden in categorias:
    try:
        cursor.execute("""
            INSERT INTO documentos_categoriadocumento
            (nombre, descripcion, icono, color, orden, activo, parent_id)
            VALUES (?, ?, ?, ?, ?, 1, NULL)
        """, (nombre, desc, icono, color, orden))
        print(f"  [OK] Insertado: {nombre}")
        categorias_insertadas += 1
    except sqlite3.IntegrityError:
        print(f"  [SKIP] Ya existe: {nombre}")

conn.commit()
print(f"\nCategorias insertadas: {categorias_insertadas}")

# Verificar totales
cursor.execute("SELECT COUNT(*) FROM documentos_tipodocumento")
total_tipos = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM documentos_categoriadocumento")
total_categorias = cursor.fetchone()[0]

conn.close()

print("\n" + "=" * 60)
print("RESUMEN FINAL")
print("=" * 60)
print(f"Total tipos de documento en BD: {total_tipos}")
print(f"Total categorias de documento en BD: {total_categorias}")
print("=" * 60)
print("\n¡Proceso completado exitosamente!")
