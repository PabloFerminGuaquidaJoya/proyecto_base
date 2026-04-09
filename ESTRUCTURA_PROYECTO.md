# 📁 Estructura del Proyecto - Sistema SENA

Documentación completa de la organización del proyecto.

## 🌳 Árbol de Directorios

```
prototipo_0.1/
└── myworld/
    └── app_prototipo/              # Proyecto Django principal
        ├── manage.py                # Comando principal Django
        ├── requirements.txt         # Dependencias del proyecto
        ├── db.sqlite3              # Base de datos SQLite
        │
        ├── 📱 APLICACIONES/MÓDULOS
        │   ├── app_prototipo/       # Configuración principal
        │   │   ├── __init__.py
        │   │   ├── settings.py      # Configuración Django
        │   │   ├── urls.py          # URLs principales
        │   │   ├── wsgi.py
        │   │   └── asgi.py
        │   │
        │   ├── usuarios/            # Gestión de usuarios
        │   │   ├──         # Usuario, Rol, Permisos
        │   │   ├── views.py         # Login, Dashboard, Perfil
        │   │   ├── forms.py
        │   │   ├── urls.py
        │   │   ├── templates/
        │   │   └── migrations/
        │   │
        │   ├── maquinaria/          # Gestión de máquinas
        │   │   ├──         # Maquina, Categoria, Alertas
        │   │   ├── views.py         # CRUD, Estadísticas
        │   │   ├── forms.py
        │   │   ├── urls.py
        │   │   ├── templates/
        │   │   └── migrations/
        │   │
        │   ├── documentos/          # Sistema de documentos ⭐ NUEVO
        │   │   ├──         # Documento, TipoDoc, Categoria
        │   │   ├── views.py         # Subir, Buscar, Descargar
        │   │   ├── forms.py         # 13 formularios
        │   │   ├── urls.py          # 40+ URLs
        │   │   ├── templates/       # 14 templates
        │   │   │   └── documentos/
        │   │   │       ├── modern_repositorio.html
        │   │   │       ├── subir_documento.html
        │   │   │       ├── detalle_documento.html
        │   │   │       ├── buscar_documentos.html
        │   │   │       ├── editar_documento.html
        │   │   │       ├── eliminar_documento.html
        │   │   │       ├── ver_documento.html
        │   │   │       ├── mis_documentos.html
        │   │   │       ├── estadisticas_documentos.html
        │   │   │       ├── categorias_documentos.html
        │   │   │       ├── tipos_documento.html
        │   │   │       ├── documentos_por_categoria.html
        │   │   │       ├── documentos_por_tipo.html
        │   │   │       └── documentos_maquina.html
        │   │   └── migrations/
        │   │
        │   ├── reportes/            # Sistema de reportes
        │   │   ├── models.py        # Reporte, TipoReporte
        │   │   ├── views.py         # Generar, Cancelar, Listar
        │   │   ├── forms.py
        │   │   ├── urls.py
        │   │   ├── templates/
        │   │   └── migrations/
        │   │
        │   ├── sistema/             # Configuración del sistema
        │   │   ├── models.py
        │   │   ├── views.py
        │   │   ├── urls.py
        │   │   └── migrations/
        │   │
        │   ├── ia_assistant/        # Asistente IA
        │   │   ├── views.py
        │   │   ├── urls.py
        │   │   └── templates/
        │   │
        │   └── api/                 # API REST
        │       ├── views.py
        │       ├── serializers.py
        │       └── urls.py
        │
        ├── 📜 SCRIPTS ORGANIZADOS    ⭐ REORGANIZADO
        │   ├── README.md            # Documentación de scripts
        │   │
        │   ├── poblacion/           # Scripts de población de BD
        │   │   ├── README.md
        │   │   ├── ejecutar_poblacion.py        ⭐ Recomendado
        │   │   ├── poblar_documentos.py
        │   │   ├── poblar_documentos.sql
        │   │   ├── crear_docs_shell.py
        │   │   ├── crear_datos_documentos.py
        │   │   ├── crear_documentos_base.py
        │   │   ├── crear_datos_iniciales.py
        │   │   ├── crear_perfil_usuario.py
        │   │   └── crear_tipos_reporte_script.py
        │   │
        │   ├── verificacion/        # Scripts de verificación
        │   │   ├── README.md
        │   │   ├── verificar_datos.py
        │   │   └── verificar_usuarios.py
        │   │
        │   └── tests/               # Scripts de testing
        │       ├── README.md
        │       └── test_endpoint.py
        │
        ├── 📄 TEMPLATES GLOBALES
        │   └── templates/
        │       ├── base.html        # Template base
        │       ├── navbar.html      # Barra de navegación
        │       └── footer.html      # Pie de página
        │
        ├── 📦 ARCHIVOS ESTÁTICOS
        │   ├── static/              # Archivos estáticos del proyecto
        │   │   ├── css/
        │   │   ├── js/
        │   │   └── img/
        │   └── staticfiles/         # Archivos estáticos recopilados
        │
        ├── 📤 MEDIA
        │   └── media/               # Archivos subidos
        │       └── documentos/      # Documentos subidos
        │           └── YYYY/MM/categoria/archivo.pdf
        │
        ├── 🔧 ENTORNO VIRTUAL
        │   └── venv/                # Virtual environment
        │       ├── Scripts/
        │       └── Lib/
        │
        └── 📚 DOCUMENTACIÓN
            ├── ESTRUCTURA_PROYECTO.md           # Este archivo
            ├── EXPLICACION_MODULO_DOCUMENTOS.txt  # Explicación detallada
            ├── INSTRUCCIONES_SETUP.md
            ├── INSTRUCCIONES_MIGRACIONES.md
            ├── ERRORES_CORREGIDOS.md
            ├── inicio_entorno.txt
            └── ejemplo_para_commit.txt
```

## 📊 Módulos del Sistema

### 1. 👥 Usuarios (`usuarios/`)
**Propósito:** Gestión de usuarios y autenticación

**Características:**
- Login/Logout
- Registro de usuarios
- Perfiles de usuario
- Gestión de roles y permisos
- Dashboard personalizado

**Modelos:**
- Usuario
- Rol
- Permiso

### 2. ⚙️ Maquinaria (`maquinaria/`)
**Propósito:** Gestión de máquinas y equipos

**Características:**
- CRUD de máquinas
- Categorización
- Seguimiento de estado
- Alertas y notificaciones
- Historial de mantenimiento

**Modelos:**
- Maquina
- CategoriaMaquina
- Alerta
- HistorialMantenimiento

### 3. 📄 Documentos (`documentos/`)
**Propósito:** Sistema de gestión documental

**Características:**
- Subida de archivos (PDF, Word, Excel, etc.)
- Búsqueda avanzada
- Categorización jerárquica
- Control de acceso por niveles
- Versionado
- Vinculación con máquinas
- Estadísticas de uso

**Modelos:**
- Documento
- TipoDocumento
- CategoriaDocumento

**URLs Principales:**
- `/documentos/` - Repositorio
- `/documentos/subir/` - Subir documento
- `/documentos/buscar/` - Búsqueda avanzada
- `/documentos/mis-documentos/` - Mis documentos
- `/documentos/estadisticas/` - Estadísticas

**Ver:** `EXPLICACION_MODULO_DOCUMENTOS.txt` para detalles completos

### 4. 📊 Reportes (`reportes/`)
**Propósito:** Generación y gestión de reportes

**Características:**
- Múltiples tipos de reportes
- Generación programada
- Exportación (PDF, Excel)
- Historial de reportes
- Cancelación de reportes

**Modelos:**
- Reporte
- TipoReporte

### 5. 🔧 Sistema (`sistema/`)
**Propósito:** Configuración y ajustes del sistema

**Características:**
- Configuraciones globales
- Parámetros del sistema
- Logs del sistema

### 6. 🤖 IA Assistant (`ia_assistant/`)
**Propósito:** Asistente inteligente

**Características:**
- Chat con IA
- Ayuda contextual
- Recomendaciones

### 7. 🌐 API (`api/`)
**Propósito:** API REST para integraciones

**Características:**
- Endpoints RESTful
- Serialización JSON
- Autenticación por token
- Documentación automática

## 🗂️ Scripts Organizados

### 📁 `scripts/poblacion/`
Scripts para insertar datos iniciales en la base de datos.

**Script Recomendado:**
- `ejecutar_poblacion.py` - Inserta tipos y categorías de documentos

**Uso:**
```bash
python scripts/poblacion/ejecutar_poblacion.py
```

### 📁 `scripts/verificacion/`
Scripts para verificar datos en la base de datos.

**Scripts:**
- `verificar_datos.py` - Verifica documentos
- `verificar_usuarios.py` - Verifica usuarios

**Uso:**
```bash
python scripts/verificacion/verificar_datos.py
```

### 📁 `scripts/tests/`
Scripts de pruebas y testing.

**Scripts:**
- `test_endpoint.py` - Prueba endpoints API

## 🚀 Comandos Principales

### Iniciar Servidor
```bash
cd myworld/app_prototipo
venv/Scripts/python manage.py runserver
```

### Crear Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### Crear Superusuario
```bash
python manage.py createsuperuser
```

### Poblar Base de Datos
```bash
python scripts/poblacion/ejecutar_poblacion.py
```

### Verificar Datos
```bash
python scripts/verificacion/verificar_datos.py
```

### Recopilar Archivos Estáticos
```bash
python manage.py collectstatic
```

## 📦 Dependencias Principales

Ver `requirements.txt` para lista completa.

**Principales:**
- Django 5.2.7
- djangorestframework
- django-cors-headers
- Pillow (imágenes)
- reportlab (PDFs)
- openpyxl (Excel)

## 🔒 Archivos Importantes

### Configuración
- `app_prototipo/settings.py` - Configuración principal
- `requirements.txt` - Dependencias
- `manage.py` - Comando Django

### Base de Datos
- `db.sqlite3` - Base de datos SQLite

### Documentación
- `ESTRUCTURA_PROYECTO.md` - Este archivo
- `EXPLICACION_MODULO_DOCUMENTOS.txt` - Módulo de documentos
- `INSTRUCCIONES_SETUP.md` - Instalación
- `INSTRUCCIONES_MIGRACIONES.md` - Migraciones
- `ERRORES_CORREGIDOS.md` - Soluciones a errores

## 🎨 Frontend

**Tecnologías:**
- Bootstrap 5
- Bootstrap Icons
- JavaScript (Vanilla)
- AJAX para interactividad

## 📱 URLs Principales

### Autenticación
- `/login/` - Iniciar sesión
- `/logout/` - Cerrar sesión
- `/registro/` - Registro de usuarios

### Dashboard
- `/` - Dashboard principal
- `/usuarios/dashboard/` - Dashboard de usuario

### Módulos
- `/maquinaria/` - Gestión de máquinas
- `/documentos/` - Sistema de documentos
- `/reportes/` - Sistema de reportes
- `/sistema/` - Configuración

### API
- `/api/` - Endpoints REST
- `/api/docs/` - Documentación API

## 🔧 Entorno de Desarrollo

### Activar Virtual Environment
```bash
# Windows
cd myworld/app_prototipo
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Variables de Entorno
Ver `inicio_entorno.txt` para configuración.

## 📝 Notas Importantes

1. **Scripts Organizados**: Todos los scripts utility están en `scripts/`
2. **Documentación Actualizada**: Ver archivos .md y .txt en raíz
3. **Módulo de Documentos**: Completamente funcional con 14 plantillas
4. **Base de Datos**: Usar scripts de población para datos iniciales
5. **Verificación**: Usar scripts de verificación después de poblar

## 🔗 Próximos Pasos

1. Revisar `INSTRUCCIONES_SETUP.md` para instalación
2. Ejecutar `scripts/poblacion/ejecutar_poblacion.py` para poblar datos
3. Acceder a `http://127.0.0.1:8000/` para usar el sistema

## 📚 Documentación Adicional

- Django: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Bootstrap 5: https://getbootstrap.com/docs/5.0/

---
**Última Actualización:** 9 de Octubre 2025
**Versión:** 0.1
**Estado:** En Desarrollo
