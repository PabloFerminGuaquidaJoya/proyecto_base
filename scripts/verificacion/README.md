# Scripts de Verificación

Scripts para verificar y validar datos en la base de datos.

## 📋 Archivos Disponibles

### `verificar_datos.py`
Verifica tipos y categorías de documentos en la base de datos.

**Muestra:**
- Todos los tipos de documento con sus propiedades
- Todas las categorías de documento
- Totales y estadísticas

**Uso:**
```bash
cd C:\INFORMACION\Desktop\prototipo_0.1\myworld\app_prototipo
python scripts/verificacion/verificar_datos.py
```

**Salida Ejemplo:**
```
============================================================
VERIFICANDO TIPOS DE DOCUMENTO
============================================================
  ID: 1 | Manual de Operación
    Descripción: Manuales de operacion y uso de maquinaria
    Icono: bi-book | Color: #007bff

Total: 8 tipos de documento

============================================================
VERIFICANDO CATEGORIAS DE DOCUMENTO
============================================================
  ID: 1 | Orden: 1 | Maquinaria
    Descripción: Documentos relacionados con maquinaria
    Icono: bi-gear-fill | Color: #007bff

Total: 8 categorías de documento
```

### `verificar_usuarios.py`
Verifica usuarios y sus perfiles en la base de datos.

**Muestra:**
- Lista de usuarios registrados
- Información de perfiles
- Estados de usuarios

**Uso:**
```bash
python scripts/verificacion/verificar_usuarios.py
```

## 🎯 Propósito

Estos scripts sirven para:

1. **Verificar población exitosa** después de ejecutar scripts de población
2. **Debugging** - Ver qué datos existen en la BD
3. **Auditoría** - Revisar integridad de datos
4. **Documentación** - Ver estructura de datos actual

## ✅ Características

- ✅ **No modifican datos** - Solo lectura
- ✅ **Seguro** - No hay riesgo de dañar la base de datos
- ✅ **Informativo** - Salida formateada y clara
- ✅ **Rápido** - Ejecución instantánea

## 🔧 Requisitos

- Base de datos SQLite (db.sqlite3) debe existir
- Ejecutar desde el directorio raíz del proyecto
- No requiere Django configurado (usa SQLite directo)

## 📊 Cuándo Usar

### Después de poblar la base de datos
```bash
# 1. Poblar
python scripts/poblacion/ejecutar_poblacion.py

# 2. Verificar
python scripts/verificacion/verificar_datos.py
```

### Para debugging
Cuando necesites ver rápidamente qué datos hay en la BD sin acceder al admin de Django.

### Antes de hacer cambios importantes
Verifica el estado actual antes de modificar la estructura de datos.

## 🚨 Solución de Problemas

### Error: "No such file or directory: db.sqlite3"
- Ejecuta desde el directorio correcto (donde está manage.py)
- Verifica que la base de datos existe

### Error: "No module named..."
- Estos scripts usan SQLite directo, no necesitan imports de Django
- Verifica que estés ejecutando el script correcto

### No se muestran datos
- La base de datos puede estar vacía
- Ejecuta primero scripts de población

## 📝 Crear Nuevos Scripts de Verificación

Template básico:

```python
import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("=" * 60)
print("VERIFICANDO [TU TABLA]")
print("=" * 60)

cursor.execute("SELECT * FROM tu_tabla ORDER BY id")
datos = cursor.fetchall()

for dato in datos:
    print(f"  ID: {dato[0]} | {dato[1]}")

print(f"\nTotal: {len(datos)} registros")

conn.close()
```

## 🔗 Ver También

- `scripts/poblacion/README.md` - Scripts para poblar datos
- `scripts/tests/README.md` - Scripts de testing
