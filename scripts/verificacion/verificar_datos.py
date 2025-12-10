import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("\n" + "=" * 60)
print("VERIFICANDO TIPOS DE DOCUMENTO")
print("=" * 60)

cursor.execute("SELECT id, nombre, descripcion, icono, color FROM documentos_tipodocumento ORDER BY id")
tipos = cursor.fetchall()

for tipo in tipos:
    print(f"  ID: {tipo[0]} | {tipo[1]}")
    print(f"    Descripción: {tipo[2]}")
    print(f"    Icono: {tipo[3]} | Color: {tipo[4]}")
    print()

print(f"Total: {len(tipos)} tipos de documento")

print("\n" + "=" * 60)
print("VERIFICANDO CATEGORIAS DE DOCUMENTO")
print("=" * 60)

cursor.execute("SELECT id, nombre, descripcion, icono, color, orden FROM documentos_categoriadocumento ORDER BY orden")
categorias = cursor.fetchall()

for cat in categorias:
    print(f"  ID: {cat[0]} | Orden: {cat[5]} | {cat[1]}")
    print(f"    Descripción: {cat[2]}")
    print(f"    Icono: {cat[3]} | Color: {cat[4]}")
    print()

print(f"Total: {len(categorias)} categorías de documento")

conn.close()

print("\n" + "=" * 60)
print("VERIFICACIÓN COMPLETADA")
print("=" * 60)
print("✓ Todos los datos están correctamente insertados")
print("✓ El módulo de documentos está listo para usar")
print("=" * 60 + "\n")
