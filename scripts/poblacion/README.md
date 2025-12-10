# Scripts de Población de Base de Datos

Scripts para insertar datos iniciales en la base de datos del sistema.

## 📋 Archivos Disponibles

### Documentos

- **`ejecutar_poblacion.py`** ⭐ RECOMENDADO
  - Inserta tipos y categorías de documentos
  - Usa SQLite directamente (más confiable)
  - 8 tipos de documento + 8 categorías

- **`poblar_documentos.py`**
  - Versión alternativa usando Django ORM

- **`poblar_documentos.sql`**
  - Script SQL directo para población

- **`crear_docs_shell.py`**
  - Para ejecutar en Django shell
  - Usa `python manage.py shell < crear_docs_shell.py`

- **`crear_datos_documentos.py`**
  - Versión anterior de población de documentos

- **`crear_documentos_base.py`**
  - Creación básica de documentos

### Usuarios

- **`crear_datos_iniciales.py`**
  - Crea datos iniciales del sistema completo

- **`crear_perfil_usuario.py`**
  - Crea perfiles de usuario de prueba

### Reportes

- **`crear_tipos_reporte_script.py`**
  - Inserta tipos de reportes en el sistema

## 🚀 Uso Recomendado

### 1. Poblar Documentos (RECOMENDADO)

```bash
cd C:\INFORMACION\Desktop\prototipo_0.1\myworld\app_prototipo
python scripts/poblacion/ejecutar_poblacion.py
```

### 2. Crear Datos Iniciales Completos

```bash
python scripts/poblacion/crear_datos_iniciales.py
```

### 3. Verificar Población

Después de ejecutar, verifica con:
```bash
python scripts/verificacion/verificar_datos.py
```

## ⚙️ Métodos de Ejecución

### Método 1: Python directo con SQLite
```python
# ejecutar_poblacion.py
import sqlite3
conn = sqlite3.connect('db.sqlite3')
# ... inserciones directas
```
✅ Más confiable, no depende de Django

### Método 2: Django ORM
```python
# poblar_documentos.py
from documentos.models import TipoDocumento
TipoDocumento.objects.create(...)
```
⚠️ Requiere Django configurado correctamente

### Método 3: Django Shell
```bash
python manage.py shell < scripts/poblacion/crear_docs_shell.py
```

### Método 4: SQL directo
```bash
sqlite3 db.sqlite3 < scripts/poblacion/poblar_documentos.sql
```

## 📊 Datos que se Insertan

### Tipos de Documento (8)
1. Manual de Operación
2. Manual de Mantenimiento
3. Ficha Técnica
4. Planos
5. Certificado
6. Procedimiento
7. Reporte
8. Otro

### Categorías de Documento (8)
1. Maquinaria
2. Seguridad
3. Calidad
4. Mantenimiento
5. Operación
6. Técnica
7. Administrativa
8. General

## ⚠️ Advertencias

- **NO ejecutar en producción** - Solo para desarrollo
- **Verificar** que la base de datos existe antes de ejecutar
- **Backup** de la base de datos antes de poblar
- Algunos scripts pueden **duplicar datos** si se ejecutan múltiples veces
- Usar `ejecutar_poblacion.py` incluye manejo de duplicados con `try-except`

## 🔍 Verificación

Después de ejecutar scripts de población, verifica con:

```bash
# Ver tipos de documento
python scripts/verificacion/verificar_datos.py

# Ver usuarios
python scripts/verificacion/verificar_usuarios.py
```

## 📝 Notas

- Los scripts usan rutas relativas, ejecuta desde la raíz del proyecto
- Si encuentras errores de "module not found", verifica que estés en el directorio correcto
- Para datos de producción, usa fixtures o Django admin
