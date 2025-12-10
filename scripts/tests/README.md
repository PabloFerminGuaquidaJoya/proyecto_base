# Scripts de Testing

Scripts para probar funcionalidades del sistema.

## 📋 Archivos Disponibles

### `test_endpoint.py`
Script para probar endpoints de la API del sistema.

**Propósito:**
- Verificar que los endpoints REST estén funcionando
- Probar respuestas de la API
- Debugging de servicios web

**Uso:**
```bash
cd C:\INFORMACION\Desktop\prototipo_0.1\myworld\app_prototipo
python scripts/tests/test_endpoint.py
```

## 🎯 Tipos de Tests

### Tests de API
- Verificación de endpoints
- Validación de respuestas JSON
- Pruebas de autenticación
- Tests de permisos

### Tests de Funcionalidad
- Probar operaciones CRUD
- Validar lógica de negocio
- Verificar cálculos y procesamiento

### Tests de Integración
- Probar flujos completos
- Verificar interacción entre módulos
- Validar datos entre tablas relacionadas

## 🚀 Cómo Ejecutar Tests

### Tests Individuales
```bash
# Test de un endpoint específico
python scripts/tests/test_endpoint.py
```

### Tests con Django
Para tests más robustos, usa el framework de testing de Django:

```bash
# Ejecutar todos los tests
python manage.py test

# Test de una app específica
python manage.py test documentos

# Test de un archivo específico
python manage.py test documentos.tests.test_models

# Test con verbosidad
python manage.py test --verbosity=2
```

## 📝 Estructura de Tests de Django

Los tests de Django deben estar en archivos `tests.py` dentro de cada app:

```
documentos/
├── tests.py              # Tests de documentos
├── test_models.py        # Tests de modelos
├── test_views.py         # Tests de vistas
└── test_forms.py         # Tests de formularios
```

## ✅ Buenas Prácticas

1. **Nombrado Claro**
   - `test_crear_documento()` ✅
   - `test1()` ❌

2. **Tests Independientes**
   - Cada test debe poder ejecutarse solo
   - No depender del orden de ejecución

3. **Usar setUp y tearDown**
   ```python
   def setUp(self):
       # Preparar datos de prueba
       self.usuario = Usuario.objects.create(...)

   def tearDown(self):
       # Limpiar después del test
       Usuario.objects.all().delete()
   ```

4. **Assertions Descriptivos**
   ```python
   self.assertEqual(
       documento.titulo,
       "Manual",
       "El título del documento debe ser 'Manual'"
   )
   ```

## 🔧 Template de Test

### Test Simple con Requests
```python
import requests

def test_endpoint():
    """Prueba un endpoint de la API"""
    url = "http://127.0.0.1:8000/api/documentos/"
    response = requests.get(url)

    assert response.status_code == 200
    print(f"✓ Endpoint responde correctamente")

    data = response.json()
    assert 'results' in data
    print(f"✓ Respuesta contiene datos")
```

### Test con Django TestCase
```python
from django.test import TestCase
from documentos.models import Documento, TipoDocumento

class DocumentoTestCase(TestCase):
    def setUp(self):
        """Preparar datos de prueba"""
        self.tipo = TipoDocumento.objects.create(
            nombre="Manual",
            tamaño_maximo_mb=50
        )

    def test_crear_documento(self):
        """Test: Crear un documento nuevo"""
        doc = Documento.objects.create(
            titulo="Manual de Prueba",
            tipo_documento=self.tipo
        )
        self.assertEqual(doc.titulo, "Manual de Prueba")
        self.assertTrue(doc.id is not None)

    def test_extension_documento(self):
        """Test: Propiedad extension() funciona"""
        doc = Documento(archivo="test.pdf")
        self.assertEqual(doc.extension, ".pdf")
```

## 🎨 Coverage (Cobertura de Tests)

Para medir cobertura de tests:

```bash
# Instalar coverage
pip install coverage

# Ejecutar tests con coverage
coverage run --source='.' manage.py test

# Ver reporte
coverage report

# Generar reporte HTML
coverage html
# Ver en: htmlcov/index.html
```

## 📊 Tipos de Tests

### Unit Tests (Unitarios)
- Prueban funciones/métodos individuales
- Aislados, rápidos
- No acceden a BD si es posible

### Integration Tests (Integración)
- Prueban interacción entre componentes
- Usan base de datos de prueba
- Verifican flujos completos

### Functional Tests (Funcionales)
- Prueban desde perspectiva del usuario
- Simulan uso real del sistema
- Pueden usar Selenium para UI

### API Tests
- Prueban endpoints REST
- Verifican respuestas JSON
- Validan códigos de estado HTTP

## 🚨 Debugging Tests

### Ver output detallado
```bash
python manage.py test --verbosity=2
```

### Mantener base de datos de test
```bash
python manage.py test --keepdb
```

### Ejecutar solo un test
```bash
python manage.py test documentos.tests.DocumentoTestCase.test_crear_documento
```

### Usar pdb (debugger)
```python
def test_algo(self):
    import pdb; pdb.set_trace()  # Breakpoint
    # ... código
```

## 📚 Recursos

- [Django Testing Docs](https://docs.djangoproject.com/en/5.2/topics/testing/)
- [Python unittest](https://docs.python.org/3/library/unittest.html)
- [pytest-django](https://pytest-django.readthedocs.io/)

## 🔗 Ver También

- `scripts/poblacion/README.md` - Poblar datos de prueba
- `scripts/verificacion/README.md` - Verificar datos
