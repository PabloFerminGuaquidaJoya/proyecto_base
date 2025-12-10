# Scripts del Proyecto

Este directorio contiene scripts utilitarios organizados por categorías.

## 📁 Estructura

```
scripts/
├── poblacion/          # Scripts para poblar la base de datos con datos iniciales
├── verificacion/       # Scripts para verificar datos en la base de datos
├── tests/              # Scripts de pruebas y testing
└── README.md          # Este archivo
```

## 📝 Descripción de Carpetas

### poblacion/
Scripts para crear e insertar datos iniciales en la base de datos.
- Datos de usuarios
- Tipos y categorías de documentos
- Tipos de reportes
- Datos de ejemplo

### verificacion/
Scripts para verificar y validar datos existentes en la base de datos.
- Verificación de usuarios
- Verificación de documentos
- Validación de integridad

### tests/
Scripts de pruebas y testing del sistema.
- Tests de endpoints API
- Tests de funcionalidad
- Scripts de debugging

## 🚀 Uso

Para ejecutar cualquier script, asegúrate de estar en el directorio raíz del proyecto:

```bash
# Desde la raíz del proyecto (donde está manage.py)
python scripts/poblacion/nombre_del_script.py
```

## ⚠️ Notas Importantes

- Algunos scripts requieren que Django esté correctamente configurado
- Ejecuta los scripts de población solo en ambientes de desarrollo
- Los scripts de verificación no modifican datos, solo los muestran
- Siempre revisa el contenido del script antes de ejecutarlo

## 📚 Documentación

Para más información sobre scripts específicos, consulta los comentarios dentro de cada archivo.
