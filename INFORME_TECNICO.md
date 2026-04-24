# INFORME TÉCNICO EXHAUSTIVO
## Sistema de Gestión de Maquinaria Pesada — SENA v2.0

**Fecha de generación:** 23 de abril de 2026  
**Versión del sistema:** 2.0  
**Framework principal:** Django 5.2.6  
**Base de datos:** MySQL 8.0 / SQLite (desarrollo)  
**Zona horaria:** America/Bogota | Idioma: es-es

---

## TABLA DE CONTENIDOS

1. [Stack Tecnológico Completo](#1-stack-tecnológico-completo)
2. [Arquitectura General](#2-arquitectura-general)
3. [Módulo: Usuarios](#3-módulo-usuarios)
4. [Módulo: Maquinaria](#4-módulo-maquinaria)
5. [Módulo: Inventario](#5-módulo-inventario)
6. [Módulo: Reportes](#6-módulo-reportes)
7. [Módulo: Documentos](#7-módulo-documentos)
8. [Módulo: Sistema](#8-módulo-sistema)
9. [Módulo: Visión Artificial](#9-módulo-visión-artificial)
10. [Módulo: API REST](#10-módulo-api-rest)
11. [Flujos de Trabajo Principales](#11-flujos-de-trabajo-principales)
12. [Relaciones entre Módulos](#12-relaciones-entre-módulos)
13. [Seguridad y Validación](#13-seguridad-y-validación)
14. [Diagrama Entidad-Relación](#14-diagrama-entidad-relación)
15. [Flujo General de la Aplicación](#15-flujo-general-de-la-aplicación)

---

## 1. Stack Tecnológico Completo

### 1.1 Dependencias Python (`requirements.txt`)

| Paquete | Propósito técnico |
|---------|-------------------|
| **Django 5.2.6** | Framework web principal — ORM, middleware, autenticación, admin, templates |
| **djangorestframework** | API REST: ViewSets, serializers, autenticación por token, paginación |
| **django-cors-headers** | Middleware CORS para peticiones cross-origin (frontend/apps móviles) |
| **django-environ** | Carga variables de entorno desde `.env` (credenciales, claves secretas) |
| **mysqlclient** | Conector nativo CPython entre Django ORM y MySQL 8.0 |
| **Pillow** | Procesamiento de imágenes: `ImageField`, redimensionamiento, conversión de formato |
| **openpyxl** | Lectura y escritura de archivos Excel `.xlsx` (importación/exportación de datos) |
| **reportlab** | Generación programática de PDFs: fichas técnicas, reportes y certificados |
| **PyMuPDF** | Extracción de texto, TOC y metadatos de archivos PDF (módulo `fitz`) |
| **python-docx** | Lectura de archivos Word `.docx`: párrafos, headings, tablas |
| **opencv-python** | Captura de cámara web, decodificación y preprocesamiento de imágenes (BGR) |
| **numpy** | Operaciones matemáticas vectoriales sobre embeddings faciales de 128 dimensiones |
| **deepface** | Extracción de embeddings faciales usando modelo Facenet con backend OpenCV |
| **tf-keras** | Backend TensorFlow/Keras requerido por DeepFace para inferencia de modelos |
| **celery** | Ejecución de tareas en segundo plano: generación de reportes, indexación |
| **redis** | Broker de mensajes para Celery + caché de sesiones, rate limiting y consultas |
| **apscheduler** | Programación de tareas periódicas: backups automáticos cada 2 horas |
| **python-dateutil** | Manejo avanzado de fechas, zonas horarias y parsing de strings de fecha |
| **requests** | Realización de peticiones HTTP externas desde el servidor |
| **qrcode[pil]** | Generación de códigos QR en formato PNG para identificación de maquinaria |

### 1.2 Configuración de Base de Datos (`settings.py`)

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME':   'proyecto_base',
        'USER':   'Root',
        'PASSWORD': '1234',
        'HOST':   'localhost',
        'PORT':   '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}
```

### 1.3 Configuración Global del Sistema

| Parámetro | Valor |
|-----------|-------|
| `DEBUG` | `True` (cambiar a `False` en producción) |
| `ALLOWED_HOSTS` | `['*']` (restringir en producción) |
| `LANGUAGE_CODE` | `'es-es'` |
| `TIME_ZONE` | `'America/Bogota'` |
| `SESSION_COOKIE_AGE` | `86400` (24 horas) |
| `EMAIL_HOST` | `smtp.gmail.com` puerto `587` (TLS) |
| `VISION_CONFIDENCE_THRESHOLD` | `0.5` |

### 1.4 Middleware Activo (orden de ejecución)

1. `corsheaders.middleware.CorsMiddleware`
2. `django.middleware.security.SecurityMiddleware`
3. `django.contrib.sessions.middleware.SessionMiddleware`
4. `django.middleware.common.CommonMiddleware`
5. `django.middleware.csrf.CsrfViewMiddleware`
6. `django.contrib.auth.middleware.AuthenticationMiddleware`
7. `django.contrib.messages.middleware.MessageMiddleware`
8. `django.middleware.clickjacking.XFrameOptionsMiddleware`

### 1.5 REST Framework

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}
```

### 1.6 Context Processors

- `usuarios.context_processors.usuario_actual` — Inyecta usuario autenticado en todas las plantillas
- `sistema.context_processors.backup_permisos` — Inyecta permisos de backup globalmente

---

## 2. Arquitectura General

```
┌──────────────────────────────────────────────────────────────┐
│                    CLIENTE (Navegador)                        │
│         Bootstrap 5.3 (local) + Vanilla JS + AJAX            │
└───────────────────────────┬──────────────────────────────────┘
                            │ HTTP/HTTPS
┌───────────────────────────▼──────────────────────────────────┐
│               DJANGO 5.2.6 — WSGI/ASGI                       │
│                                                               │
│  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌────────────────┐  │
│  │ usuarios │ │ maquinaria│ │reportes  │ │   sistema      │  │
│  └──────────┘ └───────────┘ └──────────┘ └────────────────┘  │
│  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌────────────────┐  │
│  │documentos│ │inventario │ │ vision   │ │   api (DRF)    │  │
│  └──────────┘ └───────────┘ └──────────┘ └────────────────┘  │
├───────────────────────────────────────────────────────────────┤
│                  ORM Django (Models)                          │
└──────────────────────┬────────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────────┐
        │              │                  │
 ┌──────▼──────┐ ┌─────▼──────┐ ┌────────▼──────┐
 │  MySQL 8.0  │ │   Redis    │ │  Sistema de   │
 │(producción) │ │ +Celery MQ │ │  archivos     │
 └─────────────┘ └────────────┘ │  /media/      │
                                └───────────────┘
```

### 2.1 Estructura de Directorios

```
proyecto_base/
├── app_prototipo/          # Configuración Django principal
│   ├── settings.py         # Toda la configuración
│   ├── urls.py             # Enrutamiento raíz
│   ├── wsgi.py / asgi.py   # Interfaces de servidor
│   └── __init__.py
├── usuarios/               # Autenticación y gestión de usuarios
├── maquinaria/             # Gestión de máquinas y mantenimiento
├── inventario/             # Piezas y componentes
├── reportes/               # Generación de reportes y métricas
├── documentos/             # Gestión documental e indexación
├── sistema/                # Configuración, backups, logs, notificaciones
├── vision/                 # Detección visual con TFLite
├── api/                    # API REST (Django REST Framework)
├── media/                  # Archivos subidos por usuarios
│   ├── backups/            # Respaldos de BD (.sql, .db)
│   ├── documentos/         # Documentos subidos
│   ├── maquinaria/         # Fotos de máquinas
│   ├── inventario/         # Fotos de piezas
│   ├── reportes/           # Reportes generados (PDF, Excel, CSV)
│   └── usuarios/fotos/     # Fotos de perfil de usuarios
├── static/                 # Archivos estáticos fuente
│   ├── css/                # Estilos personalizados + Bootstrap 5.3 (local)
│   ├── js/                 # Scripts + Bootstrap Bundle (local)
│   └── vendor/             # Bootstrap Icons 1.10 (local con fuentes)
├── staticfiles/            # Archivos estáticos recopilados (collectstatic)
├── scripts/                # Scripts de utilidad y población de BD
│   ├── poblacion/          # Carga de datos iniciales
│   └── verificacion/       # Scripts de verificación de integridad
├── manage.py               # CLI de Django
└── requirements.txt
```

---

## 3. Módulo: Usuarios

**App Django:** `usuarios`  
**Propósito:** Gestión integral de usuarios, autenticación por contraseña, autenticación por reconocimiento facial y control de roles y permisos.

### 3.1 Modelos

#### `TipoUsuario`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `nombre` | `CharField(100, unique)` | Nombre del rol (Administrador, Instructor, Aprendiz…) |
| `descripcion` | `TextField` | Descripción funcional del rol |
| `permisos` | `JSONField` | Mapa JSON de permisos granulares por módulo |
| `activo` | `BooleanField(default=True)` | Si el rol está habilitado |
| `created_at / updated_at` | `DateTimeField(auto_now)` | Timestamps automáticos |

#### `Usuario` (modelo principal)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `tipo_documento` | `CharField choices` | CC, TI, CE, PAS |
| `numero_documento` | `CharField(unique)` | Validado por regex (solo dígitos) |
| `nombres / apellidos` | `CharField` | Auto-capitalizados en `save()` |
| `email` | `EmailField(unique)` | Correo electrónico único |
| `telefono` | `CharField` | Número de contacto |
| `foto_perfil` | `ImageField` | `upload_to='usuarios/fotos/'` |
| `tipo_usuario` | `FK → TipoUsuario (PROTECT)` | Rol asignado |
| `centro_formacion` | `FK → CentroFormacion (SET_NULL)` | Centro asignado |
| `ficha` | `FK → Ficha (SET_NULL)` | Solo para aprendices |
| `estado` | `CharField choices` | `activo / inactivo / suspendido / pendiente` (default: `pendiente`) |
| `fecha_registro` | `DateTimeField(auto_now_add)` | Fecha de creación |
| `fecha_aprobacion` | `DateTimeField(null)` | Cuándo fue aprobado por admin |
| `ultimo_acceso` | `DateTimeField(null)` | Último inicio de sesión |
| `created_by` | `FK → self (SET_NULL)` | Usuario que creó este registro |
| Índices | — | `numero_documento`, `email`, `estado` |

#### `SesionUsuario`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `usuario` | `FK → Usuario (CASCADE)` | Usuario de la sesión |
| `token_sesion` | `CharField(unique)` | Token único de sesión |
| `ip_address` | `GenericIPAddressField` | IP de origen |
| `user_agent` | `TextField` | Navegador y SO del cliente |
| `fecha_inicio` | `DateTimeField(auto_now_add)` | Inicio de sesión |
| `fecha_fin` | `DateTimeField(null)` | Cierre de sesión |
| `activa` | `BooleanField` | Si la sesión está activa |

#### `TokenRecuperacionPassword`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `usuario` | `FK → Usuario (CASCADE)` | Propietario del token |
| `token` | `CharField(unique)` | `secrets.token_urlsafe(32)` (43 chars Base64-URL-safe) |
| `fecha_expiracion` | `DateTimeField` | `now() + 1 hora` |
| `usado` | `BooleanField` | Se marca `True` después de uso |
| `ip_solicitud` | `GenericIPAddressField` | IP desde donde se solicitó |
| Métodos | — | `es_valido()`, `esta_expirado()` |

#### `ReconocimientoFacial`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `usuario` | `OneToOneField → Usuario (CASCADE)` | Un embedding por usuario |
| `embedding` | `JSONField` | Vector de 128 floats (Facenet) |
| `activo` | `BooleanField` | Si está habilitado para autenticación |
| `confianza_registro` | `FloatField(0–1)` | Confianza al momento del registro |
| `ip_registro / user_agent_registro` | `CharField` | Auditoría del registro |

#### `IntentoReconocimientoFacial`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `usuario` | `FK → Usuario (SET_NULL)` | `NULL` si no se identificó |
| `tipo_intento` | `choices` | `registro / login / actualizacion` |
| `resultado` | `choices` | `exitoso / fallido / error` |
| `similitud` | `FloatField(0–1)` | Similitud coseno calculada |
| `mensaje_error` | `TextField` | Razón del fallo (si aplica) |
| `fecha_intento` | `DateTimeField(auto_now_add)` | Timestamp |
| `ip_address / user_agent` | `CharField` | Auditoría |
| Índices | — | `(usuario, -fecha_intento)`, `(resultado, -fecha_intento)` |

### 3.2 Backend de Autenticación (`authentication.py`)

**`UsuarioBackend`** (hereda de `ModelBackend`):

```
authenticate(request, username, password):
  1. Busca Usuario por numero_documento O email
  2. Sincroniza DjangoUser:
     - is_staff = True si tipo_usuario.nombre contiene 'administrador' o 'staff'
     - is_active = True si estado in ('activo', 'pendiente')
  3. Valida password con PBKDF2-SHA256
  4. Retorna usuario Django si válido, None si no
```

### 3.3 Reconocimiento Facial (`facial_recognition.py`)

**Clase `FacialRecognitionService`:**

| Parámetro | Valor |
|-----------|-------|
| `MODEL_NAME` | `"Facenet"` (128D embeddings) |
| `DETECTOR_BACKEND` | `"opencv"` |
| `THRESHOLD_SIMILITUD` | `0.6` (similitud coseno mínima) |
| `DISTANCE_METRIC` | `"cosine"` |

**Métodos clave:**

| Método | Descripción |
|--------|-------------|
| `decode_base64_image(b64)` | Convierte base64 → `np.ndarray BGR` |
| `detectar_rostro(imagen)` | Detecta exactamente 1 rostro (confidence > 0.5) |
| `extraer_embedding(imagen)` | Extrae vector 128D con `DeepFace.represent()` |
| `calcular_similitud(emb1, emb2)` | Similitud coseno normalizada a `[0, 1]` |
| `verificar_autenticacion(cap, alm)` | `True` si similitud ≥ THRESHOLD |
| `validar_calidad_imagen(img)` | Resolución mín. 320×240, brillo entre 40 y 220 |

### 3.4 Validación de Contraseñas (`validators.py`)

**`ComplejidadPasswordValidator`**:
- Mínimo **8 caracteres**
- Al menos **1 mayúscula**
- Al menos **1 minúscula**
- Al menos **1 número**
- Al menos **1 símbolo especial** (`!@#$%^&*...`)

**Hashers configurados:**
1. `PBKDF2PasswordHasher` (primario, 260.000 iteraciones)
2. `PBKDF2SHA1PasswordHasher` (legado)

### 3.5 Vistas Principales

| Vista | Ruta | Descripción |
|-------|------|-------------|
| `login_view` | `/usuarios/login/` | Autenticación por contraseña |
| `register_view` | `/usuarios/register/` | Registro público (estado inicial: `pendiente`) |
| `logout_view` | `/usuarios/logout/` | Cierra sesión y marca `SesionUsuario.activa=False` |
| `dashboard_view` | `/usuarios/dashboard/` | Panel principal con estadísticas |
| `perfil_view` | `/usuarios/perfil/` | Visualización y edición del perfil propio |
| `centro_control_view` | `/usuarios/centro-control/` | Panel administrativo (solo staff) |
| `recuperar_password_view` | `/usuarios/recuperar-password/` | Inicio del flujo de recuperación |
| `reset_password_view` | `/usuarios/reset-password/<token>/` | Reset con token válido |
| `registrar_rostro_view` | `/usuarios/api/registrar-rostro/` | POST: captura y guarda embedding facial |
| `login_facial_view` | `/usuarios/api/login-facial/` | POST: autenticación por reconocimiento facial |

### 3.6 Rate Limiting (Login Facial)

- **Máximo:** 5 intentos en 5 minutos por IP
- **Implementación:** `django.core.cache` con clave `facial_login_attempts_{ip}`
- Después del límite: respuesta `429 Too Many Requests`

---

## 4. Módulo: Maquinaria

**App Django:** `maquinaria`  
**Propósito:** Gestión del ciclo de vida completo de máquinas: registro, estados, alertas, historial, mantenimiento programado y eliminación con backup histórico.

### 4.1 Modelos

#### `CategoriaMaquina`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `nombre` | `CharField(unique)` | Nombre de la categoría |
| `icono` | `CharField` | Bootstrap Icon (`bi-*`) |
| `color` | `CharField(hex)` | Color representativo |
| `activa` | `BooleanField` | Si está disponible para asignar |

#### `Proveedor`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `nombre` | `CharField` | Nombre del proveedor |
| `nit` | `CharField(unique)` | NIT empresarial |
| `contacto_nombre / telefono / email` | `CharField / EmailField` | Datos de contacto |
| `calificacion` | `IntegerField(1–5)` | Calificación del proveedor |

#### `Maquina` (modelo central)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `codigo_inventario` | `CharField(unique)` | Código único de inventario |
| `numero_serie` | `CharField(unique)` | Número de serie del fabricante |
| `estado` | `choices` | `disponible / operativa / mantenimiento / reparacion / fuera_servicio / retirada` |
| `categoria` | `FK → CategoriaMaquina (PROTECT)` | Tipo de máquina |
| `proveedor` | `FK → Proveedor (SET_NULL)` | Proveedor de adquisición |
| `responsable` | `FK → Usuario (SET_NULL)` | Técnico o instructor responsable |
| `horas_uso_total / horas_uso_mes` | `DecimalField` | Horas de operación |
| `fecha_ultimo_mantenimiento / proximo_mantenimiento` | `DateField(null)` | Control de mantenimiento |
| `frecuencia_mantenimiento_dias` | `IntegerField(default=90)` | Periodicidad de mantenimiento |
| `imagen / manual_pdf / ficha_tecnica` | `ImageField / FileField` | Archivos asociados |
| `qr_code` | `CharField(500)` | URL codificada en el QR generado |
| `created_by` | `FK → Usuario (SET_NULL)` | Quién registró la máquina |
| Propiedades | `@property` | `necesita_mantenimiento`, `tiempo_sin_mantenimiento` |

#### `AlertaMaquina`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `tipo` | `choices` | `mantenimiento / reparacion / eficiencia / uso_excesivo / garantia / inspeccion` |
| `prioridad` | `choices` | `baja / media / alta / critica` |
| `estado` | `choices` | `activa / en_proceso / resuelta / ignorada` |
| `resuelto_por` | `FK → Usuario (SET_NULL)` | Quién resolvió la alerta |
| `notas_resolucion` | `TextField` | Descripción de la resolución |
| Índices | — | `(estado)`, `(prioridad)`, `(tipo)` |

#### `HistorialMaquina`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `tipo_evento` | `choices` | `creacion / mantenimiento / reparacion / cambio_estado / cambio_ubicacion / cambio_responsable / actualizacion / inspeccion / alerta_creada / alerta_resuelta / eliminacion` |
| `valor_anterior / valor_nuevo` | `TextField` | Estado antes y después del cambio |
| `costo_asociado` | `DecimalField(null)` | Costo del evento si aplica |
| `archivos_adjuntos` | `JSONField(default=list)` | Lista de archivos adjuntos |
| Índices | — | `(maquina, -fecha_evento)`, `(tipo_evento)` |

#### `MantenimientoProgramado`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `tipo` | `choices` | `preventivo / correctivo / predictivo / urgente / emergencia` |
| `prioridad` | `choices` | `baja / media / alta / critica / emergencia` |
| `estado` | `choices` | `programado / en_progreso / completado / cancelado / postergado` |
| `tecnico_asignado` | `FK → Usuario (SET_NULL)` | Técnico planificado |
| `tecnico_realizado` | `FK → Usuario (SET_NULL)` | Técnico que ejecutó |
| `personal_adicional` | `ManyToManyField → Usuario` | Equipo adicional |
| `componentes_revisar / herramientas_necesarias / repuestos_necesarios` | `JSONField` | Listas de trabajo |
| `costo_estimado / costo_real / costo_repuestos / costo_mano_obra` | `DecimalField` | Desglose de costos |
| `proximo_mantenimiento` | `DateField` | Fecha del siguiente mantenimiento |
| Método | `marcar_completado(usuario)` | Completa el mantenimiento y actualiza historial |

#### `MaquinaEliminada` (archivo histórico)
Almacena un **backup JSON completo** de la máquina antes de ser eliminada:
- `datos_completos_maquina` — JSON con todos los campos
- `historial_completo` — JSON con todo el historial
- `alertas_asociadas` — JSON con todas las alertas
- `mantenimientos_realizados` — JSON con todos los mantenimientos
- Estadísticas calculadas: `total_mantenimientos`, `costo_total_mantenimiento`, `dias_operacion`

#### `UsoMaquinaria`
Registro de cada sesión de uso en práctica de formación:
- `instructor_encargado`, `ficha`, `fecha`, `hora_inicio/fin`, `horas_uso`, `descripcion_actividad`

#### `ObjetoMaquinaria`
Componentes individuales de máquinas con **6 fotos angulares** (frontal, lateral derecha, lateral izquierda, trasera, superior, inferior) para reconocimiento visual.

### 4.2 Vistas Principales

| Vista | Descripción |
|-------|-------------|
| `dashboard_view` | Estadísticas generales + últimas alertas + lista de máquinas |
| `crear_maquina_view` | Crea máquina y registra evento de creación en historial |
| `editar_maquina_view` | Detecta campos modificados y registra en historial |
| `eliminar_maquina_view` | Crea `MaquinaEliminada` con backup completo antes de borrar |
| `cambiar_estado_maquina` | Registra `HistorialMaquina('cambio_estado')` con valores anterior/nuevo |
| `generar_qr_maquina` | Genera imagen PNG del QR con URL a `info_qr_maquina` |
| `info_qr_maquina` | Página de información accesible por QR con datos reales |
| `programar_mantenimiento_view` | Crea `MantenimientoProgramado` y calcula próximo mantenimiento |
| `mantenimiento_dashboard_view` | Dashboard de carga de trabajo de técnicos y próximos mantenimientos |
| `alertas_view` | Listado con filtros de alertas activas y resueltas |
| `resolver_alerta` | Marca alerta como resuelta y registra en historial |

### 4.3 URL Routing (`urls.py`) — 60+ rutas

```
/maquinaria/dashboard/              → dashboard_view
/maquinaria/lista/                  → lista_maquinas_view
/maquinaria/crear/                  → crear_maquina_view
/maquinaria/detalle/<pk>/           → detalle_maquina_view
/maquinaria/editar/<pk>/            → editar_maquina_view
/maquinaria/eliminar/<pk>/          → eliminar_maquina_view
/maquinaria/cambiar-estado/<pk>/    → cambiar_estado_maquina
/maquinaria/historial/<pk>/         → historial_maquina_view
/maquinaria/qr/<pk>/                → generar_qr_maquina  (retorna imagen PNG)
/maquinaria/qr-info/<codigo>/       → info_qr_maquina  (página de info por QR)
/maquinaria/alertas/                → alertas_view
/maquinaria/alertas/crear/          → crear_alerta_view
/maquinaria/alertas/resolver/<pk>/  → resolver_alerta
/maquinaria/mantenimiento/          → mantenimiento_dashboard_view
/maquinaria/mantenimiento/programar/<pk>/ → programar_mantenimiento_view
/maquinaria/importar/               → importar_maquinas_view
/maquinaria/exportar/               → exportar_maquinas_view
```

---

## 5. Módulo: Inventario

**App Django:** `inventario`  
**Propósito:** Gestión de piezas, repuestos y componentes de maquinaria con control de estado y alertas de vida útil.

### 5.1 Modelo `PiezaInventario`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `codigo_inventario` | `CharField(unique)` | Código único de la pieza |
| `condicion` | `choices` | `nueva / usada / cambiada / dañada` |
| `horas_uso / horas_uso_maximas` | `DecimalField(default=0)` | Control de vida útil |
| `responsable` | `FK → Usuario (SET_NULL)` | Responsable de la pieza |
| `maquina` | `FK → Maquina (SET_NULL)` | Máquina a la que pertenece (opcional) |
| `foto_pieza / foto_empaque` | `ImageField` | Fotos desde galería |
| `foto_frontal/lateral_derecha/lateral_izquierda/trasera/superior/inferior` | `ImageField` | 6 ángulos capturados desde cámara web |
| `@property tiene_alerta` | `bool` | `True` si `condicion='dañada'` OR `horas_uso >= horas_uso_maximas` |

### 5.2 Vistas

- `dashboard_inventario_view` — Estadísticas y lista filtrada
- `nueva_pieza_view` — Captura 6 fotos desde cámara web (base64 → `ImageField`)
- `editar_pieza_view` — Actualización con posibilidad de recapturar fotos
- `lista_piezas_view` — Filtros por condición y búsqueda; alertas visuales destacadas

---

## 6. Módulo: Reportes

**App Django:** `reportes`  
**Propósito:** Generación bajo demanda de reportes en múltiples formatos y cálculo de métricas de rendimiento del sistema.

### 6.1 Modelos

#### `TipoReporte`
Define plantillas de reportes: nombre, `parametros_requeridos` (JSON), `formato_salida` (JSON con lista de formatos permitidos).

#### `Reporte` (PK: UUID)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `UUIDField(primary_key)` | Identificador único |
| `tipo_reporte` | `FK → TipoReporte (PROTECT)` | Plantilla aplicada |
| `formato` | `choices` | `pdf / excel / csv / json` |
| `estado` | `choices` | `pendiente / generando / completado / error / cancelado` |
| `parametros` | `JSONField` | Filtros aplicados |
| `fecha_inicio / fecha_fin` | `DateField` | Rango temporal del reporte |
| `archivo_resultado` | `FileField` | `upload_to='reportes/resultados/'` |
| `tamaño_archivo` | `BigIntegerField` | Bytes del archivo generado |
| `total_registros` | `IntegerField` | Cantidad de registros procesados |
| `tiempo_procesamiento` | `DurationField` | Duración del proceso |
| `veces_descargado` | `IntegerField` | Contador de descargas |
| Índices | — | `(usuario_solicitante, -fecha_solicitud)`, `(estado)` |

#### `MetricasRendimiento`
Métricas calculadas automáticamente por período (`diario / semanal / mensual / anual`) para cada centro y categoría de máquina:
- Disponibilidad operacional, eficiencia promedio, horas de uso
- Tasas de mantenimiento y reparación, costos totales
- Generación y resolución de alertas

### 6.2 Formatos de Salida

| Formato | Librería | Descripción |
|---------|---------|-------------|
| PDF | `reportlab` | Reportes formateados con tablas y estilos corporativos |
| Excel (.xlsx) | `openpyxl` | Hojas de cálculo con datos tabulares y formato |
| CSV | `csv` (stdlib) | Datos planos para integración con terceros |
| JSON | `json` (stdlib) | Respuesta estructurada para APIs |

---

## 7. Módulo: Documentos

**App Django:** `documentos`  
**Propósito:** Repositorio centralizado de documentos técnicos con extracción automática de contenido, control de acceso granular y búsqueda full-text.

### 7.1 Modelos

#### `TipoDocumento`
Define tipos de documento con extensiones permitidas y tamaño máximo en MB.  
**8 tipos predefinidos:** Manual, Ficha Técnica, Planos, Procedimientos, Certificados, Normativas, Contratos, Otros.

#### `CategoriaDocumento` (Jerárquica)
- `parent (FK → self, null)` — Permite árbol de categorías de profundidad ilimitada
- `@property nivel` — Calcula profundidad del nodo en el árbol

#### `Documento` (PK: UUID)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `UUIDField(primary_key)` | Identificador único |
| `tipo_documento` | `FK → TipoDocumento (PROTECT)` | Tipo asignado |
| `categoria` | `FK → CategoriaDocumento (PROTECT)` | Categoría del árbol |
| `archivo` | `FileField` | `upload_to=documento_upload_path` |
| `checksum` | `CharField` | SHA-256 del archivo (integridad) |
| `nivel_acceso` | `choices` | `publico / interno / confidencial / restringido` |
| `usuarios_acceso` | `ManyToManyField → Usuario` | Para nivel `restringido` |
| `estado` | `choices` | `borrador / revision / aprobado / publicado / archivado / obsoleto` |
| `contenido_texto` | `TextField` | Texto extraído (PDF: PyMuPDF, DOCX: python-docx) |
| `indices_busqueda` | `JSONField` | Headings y palabras clave indexados |
| `maquina_relacionada` | `FK → Maquina (CASCADE)` | Documento técnico de una máquina específica |
| `total_descargas / total_visualizaciones` | `IntegerField` | Estadísticas de uso |

### 7.2 Extracción Automática de Contenido

```
Al subir documento:
  Si .pdf  → PyMuPDF (fitz):
    - doc.get_toc()       → Índice del documento
    - page.get_text()     → Texto completo
    - doc.metadata        → Metadatos del PDF
  
  Si .docx → python-docx:
    - doc.paragraphs      → Todos los párrafos
    - paragraph.style     → Headings (Heading 1, 2, 3...)
    - table.rows          → Contenido de tablas
  
  Resultado:
    - contenido_texto = texto completo (para búsqueda)
    - indices_busqueda = {headings: [...], palabras_clave: [...]}
    - checksum = SHA256(archivo.read())
```

---

## 8. Módulo: Sistema

**App Django:** `sistema`  
**Propósito:** Administración del sistema: configuración global, backups automáticos, logs de auditoría, notificaciones y gestión de centros de formación.

### 8.1 Modelos

#### `Configuracion`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `clave` | `CharField(unique)` | Identificador de la configuración |
| `valor` | `TextField` | Valor almacenado como string |
| `tipo_valor` | `choices` | `string / integer / float / boolean / json / date / datetime / email / url` |
| `publico` | `BooleanField` | Si es accesible desde el frontend |
| `get_valor_typed()` | Método | Convierte `valor` al tipo nativo según `tipo_valor` |

#### `Notificacion` (PK: UUID)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `usuario` | `FK → Usuario (CASCADE)` | Destinatario |
| `tipo` | `choices` | `info / success / warning / error / system` |
| `estado` | `choices` | `pendiente / enviada / leida / archivada` |
| `requiere_accion` | `BooleanField` | Si necesita acción del usuario |
| `url_accion / texto_accion` | `CharField` | Botón de acción en la notificación |
| `maquina_relacionada` | `FK → Maquina (CASCADE)` | Contexto de maquinaria (opcional) |
| `alerta_relacionada` | `FK → AlertaMaquina (CASCADE)` | Contexto de alerta (opcional) |
| Índices | — | `(usuario, estado)`, `(fecha_creacion)`, `(tipo)` |

#### `LogActividad` (PK: UUID)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `nivel` | `choices` | `debug / info / warning / error / critical` |
| `modulo` | `choices` | `usuarios / maquinaria / reportes / documentos / sistema / backups / api` |
| `accion` | `CharField` | Ej: `"usuario.crear"`, `"maquina.editar"` |
| `objeto_tipo / objeto_id` | `CharField` | Modelo y PK del objeto afectado |
| `request_method / request_path` | `CharField` | Método y ruta HTTP |
| `tiempo_ejecucion` | `DurationField` | Tiempo de procesamiento de la vista |
| Índices | — | `(timestamp)`, `(usuario, timestamp)`, `(modulo, timestamp)`, `(accion)` |

#### `BackupDatabase` (PK: UUID)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `tipo` | `choices` | `manual / automatico / programado` |
| `estado` | `choices` | `creando / completado / error / restaurando / restaurado` |
| `archivo` | `FileField` | `upload_to='backups/%Y/%m/'` |
| `tamaño_bytes` | `BigIntegerField` | Tamaño del archivo de backup |
| `total_tablas / total_registros` | `IntegerField` | Estadísticas del dump |
| `version_django / version_python` | `CharField` | Versiones al momento del backup |
| `@property puede_restaurar` | `bool` | `estado in ('completado', 'restaurado') AND archivo.exists()` |

#### Modelos de Centros de Formación

| Modelo | Descripción |
|--------|-------------|
| `CentroFormacion` | Centro de formación SENA |
| `AmbienteFormacion` | Sala o taller dentro de un centro |
| `Ficha` | Grupo o cohorte de aprendices (`numero` único) |

### 8.2 Backup Automático (APScheduler)

```
Programado: cada 2 horas
  → Crea BackupDatabase (estado='creando')
  → mysqldump (o SQLite dump) de la base de datos
  → Comprime en .sql.gz
  → Guarda en /media/backups/%Y/%m/
  → BackupDatabase.estado = 'completado'
  → Registra en LogActividad (modulo='backups')
```

---

## 9. Módulo: Visión Artificial

**App Django:** `vision`  
**Propósito:** Detección automática de maquinaria pesada mediante un modelo de inteligencia artificial TensorFlow Lite.

### 9.1 Configuración del Modelo (`settings.py`)

```python
VISION_MODEL_PATH = BASE_DIR / 'vision' / 'models' / 'heavy_machinery.tflite'
VISION_LABELS_PATH = BASE_DIR / 'vision' / 'models' / 'labels.txt'
VISION_CONFIDENCE_THRESHOLD = 0.5
```

### 9.2 Mapeo de Clases (`detector.py`)

**Clases de maquinaria detectadas:**

| Clase interna | Categoría asignada |
|---------------|-------------------|
| `excavadora` | Maquinaria de Excavación y Movimiento de Tierras |
| `bulldozer` | Maquinaria de Excavación y Movimiento de Tierras |
| `retroexcavadora` | Maquinaria de Excavación y Movimiento de Tierras |
| `grua_torre / grua_movil` | Maquinaria de Elevación y Izaje |
| `compactadora / motoniveladora / pavimentadora` | Maquinaria de Nivelación y Compactación |
| `cargador_frontal / camion_minero / volquete` | Maquinaria de Carga y Transporte |
| `perforadora` | Maquinaria de Perforación |

**Componentes detectados (no son máquinas completas):**  
`cucharon, orugas, brazo_hidraulico, cabina_operador, hoja_topadora, contrapeso, pluma_grua, neumatico_pesado, cilindro_hidraulico, motor_diesel, tren_de_rodaje, gancho_grua, cucharona_cargador`

### 9.3 Pipeline de Detección

```
detectar(imagen_bytes):
  1. Si modelo no disponible → retorna {modelo_disponible: False}
  2. Decodifica bytes → np.ndarray BGR (OpenCV)
  3. Convierte BGR → RGB
  4. Redimensiona a 224×224 (entrada del modelo TFLite)
  5. Normaliza valores a [0, 1] (float32)
  6. Inferencia TFLite (invoke)
  7. Extrae output_data, ordena por confianza
  8. Si max_confianza < THRESHOLD (0.5) → detectado=False
  9. Mapea clase → categoría_maquina
  10. Retorna {detectado, clase, clase_display, confianza, categoria_maquina,
              es_componente, top3, mensaje}
```

### 9.4 API Endpoints de Visión

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/vision/api/detectar/` | Envía imagen, retorna JSON con detección |
| `GET` | `/vision/api/estado/` | Estado del sistema de visión (modelo disponible, umbral, clases) |

---

## 10. Módulo: API REST

**App Django:** `api`  
**Framework:** Django REST Framework  
**Autenticación:** `TokenAuthentication` + `SessionAuthentication`  
**Paginación:** 50 registros por página

### 10.1 ViewSets (CRUD completo)

| ViewSet | Endpoint base | Filtros |
|---------|--------------|---------|
| `MaquinaViewSet` | `/api/maquinas/` | `categoria`, `estado`, `centro` |
| `AlertaMaquinaViewSet` | `/api/alertas/` | `estado` |

### 10.2 Endpoints Especializados

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/auth/token/` | Obtener token de acceso |
| `POST` | `/api/auth/login/` | Login con credenciales |
| `POST` | `/api/auth/logout/` | Invalidar token |
| `GET` | `/api/maquinas/buscar/?q=…` | Búsqueda de maquinaria |
| `GET` | `/api/maquinas/<id>/historial/` | Historial de una máquina |
| `POST` | `/api/maquinas/<id>/cambiar-estado/` | Cambiar estado de máquina |
| `GET` | `/api/alertas/activas/` | Solo alertas con estado `activa` |
| `POST` | `/api/alertas/<id>/resolver/` | Resolver alerta |
| `POST` | `/api/reportes/generar/` | Solicitar generación de reporte |
| `GET` | `/api/reportes/<uuid>/descargar/` | Descargar reporte generado |
| `GET` | `/api/dashboard/datos/` | Datos agregados del dashboard |
| `GET` | `/api/metricas/resumen/` | Resumen de métricas de rendimiento |
| `GET` | `/api/estadisticas/generales/` | Estadísticas globales del sistema |
| `GET` | `/api/status/` | Estado general del sistema |
| `POST` | `/api/bulk/importar-maquinas/` | Importación masiva Excel/CSV |
| `GET` | `/api/bulk/exportar-maquinas/` | Exportación masiva Excel/CSV |

### 10.3 Formato de Respuesta de Error

```json
{
  "error": "Descripción del error",
  "detail": "Detalle técnico adicional",
  "code": "error_code_string"
}
```

---

## 11. Flujos de Trabajo Principales

### 11.1 Registro y Autenticación

```
REGISTRO PÚBLICO
  /usuarios/register/ → RegistroUsuarioForm (tipos: Invitado, Aprendiz, Instructor)
  → Valida: numero_documento único, email único, contraseña compleja
  → Crea Usuario (estado='pendiente')
  → Crea DjangoUser (password=PBKDF2-SHA256)
  → Envía email de bienvenida (SMTP Gmail)
  → Admin aprueba → estado='activo', fecha_aprobacion=now()

LOGIN ESTÁNDAR
  POST /usuarios/login/ (numero_documento o email + password)
  → UsuarioBackend.authenticate()
    ├─ Busca por numero_documento O email
    ├─ Sincroniza DjangoUser (is_staff, is_active)
    └─ Valida password PBKDF2
  → login() → crea sesión Django
  → Crea SesionUsuario (token único, IP, user_agent)
  → Actualiza usuario.ultimo_acceso
  → Redirige a /usuarios/dashboard/

LOGIN FACIAL
  POST /usuarios/api/login-facial/ (numero_documento + imagen_base64)
  → Rate limiting (máx 5 intentos / 5 min / IP)
  → Busca ReconocimientoFacial activo del usuario
  → Decodifica imagen base64 → np.ndarray
  → Valida calidad (resolución, brillo)
  → Extrae embedding con DeepFace (Facenet)
  → Calcula similitud coseno con embedding almacenado
  → Si similitud ≥ 0.6:
      ├─ Crea sesión Django
      ├─ Crea SesionUsuario
      └─ Registra IntentoReconocimientoFacial(resultado='exitoso')
  → Si similitud < 0.6:
      └─ Registra IntentoReconocimientoFacial(resultado='fallido', similitud)
  → Retorna JSON {success, redirect_url}

LOGOUT
  → SesionUsuario.activa = False
  → django.auth.logout()
  → Redirige a login
```

### 11.2 Gestión de Maquinaria

```
CREAR MÁQUINA
  POST /maquinaria/crear/
  → Valida codigo_inventario y numero_serie únicos
  → Crea Maquina (created_by=usuario_actual)
  → Crea HistorialMaquina(tipo_evento='creacion')
  → Redirige a detalle

EDITAR MÁQUINA
  POST /maquinaria/editar/<pk>/
  → Detecta exactamente qué campos cambiaron
  → Actualiza Maquina
  → Crea HistorialMaquina(tipo_evento='actualizacion', campos_cambiados)

CAMBIAR ESTADO
  POST /maquinaria/cambiar-estado/<pk>/
  → valor_anterior = maquina.estado
  → maquina.estado = nuevo_estado
  → Crea HistorialMaquina('cambio_estado', valor_anterior, nuevo_estado)
  → Retorna JSON success

ELIMINAR (SOFT DELETE + BACKUP COMPLETO)
  POST /maquinaria/eliminar/<pk>/ (motivo_eliminacion)
  → Recopila: máquina, historial[], alertas[], mantenimientos[]
  → Crea MaquinaEliminada (JSONField con todo)
  → Calcula estadísticas finales (costos, días operación)
  → Crea HistorialMaquina('eliminacion')  ← ANTES de eliminar
  → maquina.delete()  ← CASCADE elimina historial, alertas, mantenimientos

CÓDIGO QR
  GET /maquinaria/qr/<pk>/
  → Construye URL absoluta a /maquinaria/qr-info/<codigo>/
  → Genera imagen QR con qrcode (PIL, PNG, 10px/box, border=4)
  → Retorna HttpResponse(content_type='image/png')
  
  GET /maquinaria/qr-info/<codigo>/
  → get_object_or_404(Maquina, codigo_inventario=codigo)
  → Carga historial (últimos 5 eventos)
  → Renderiza info_qr.html con datos reales
```

### 11.3 Generación de Reportes

```
POST /reportes/generar/
  → Crea Reporte (estado='pendiente', UUID)
  → Si Celery disponible:
      ├─ Encola tarea asincrónica
      └─ Estado = 'generando'
  → Si sincrónico:
      ├─ Consulta BD con filtros
      ├─ Genera archivo (reportlab/openpyxl/csv)
      ├─ archivo_resultado = FileField
      ├─ Estado = 'completado'
      └─ total_registros = count()

GET /reportes/<uuid>/descargar/
  → Valida acceso (usuario_solicitante o admin)
  → veces_descargado += 1
  → fecha_ultima_descarga = now()
  → Retorna FileResponse (Content-Disposition: attachment)
```

### 11.4 Gestión Documental

```
POST /documentos/crear/
  → Valida: extensión en tipo.extensiones_permitidas, tamaño ≤ tipo.tamaño_maximo_mb
  → Calcula SHA256 del archivo
  → Crea Documento (estado='borrador', creado_por=usuario)
  → Extrae contenido según tipo:
      ├─ .pdf  → PyMuPDF: contenido_texto + indices_busqueda
      └─ .docx → python-docx: párrafos + headings

CONTROL DE ACCESO EN CONSULTA
  → 'publico'      → todos los usuarios
  → 'interno'      → solo usuarios autenticados activos
  → 'confidencial' → solo administradores/coordinadores
  → 'restringido'  → solo usuarios en documento.usuarios_acceso (M2M)
```

---

## 12. Relaciones entre Módulos

```
USUARIOS
  ├─→ FK en Maquina (responsable, created_by)
  ├─→ FK en MantenimientoProgramado (tecnico_asignado, tecnico_realizado)
  ├─→ M2M en MantenimientoProgramado (personal_adicional)
  ├─→ FK en UsoMaquinaria (instructor_encargado, registrado_por)
  ├─→ FK en PiezaInventario (responsable, registrado_por)
  ├─→ FK en Documento (creado_por, modificado_por)
  ├─→ M2M en Documento (usuarios_acceso)
  ├─→ FK en Reporte (usuario_solicitante)
  ├─→ FK en BackupDatabase (creado_por, restaurado_por)
  ├─→ FK en Notificacion (usuario)
  └─→ FK en LogActividad (usuario)

MAQUINARIA
  ├─→ Documentos relacionados (FK Maquina desde Documento)
  ├─→ Alertas (AlertaMaquina 1:N)
  ├─→ Historial (HistorialMaquina 1:N)
  ├─→ Mantenimientos (MantenimientoProgramado 1:N)
  ├─→ Usos (UsoMaquinaria 1:N)
  ├─→ Objetos/Piezas (ObjetoMaquinaria 1:N)
  ├─→ Inventario (PiezaInventario N:1)
  ├─→ Notificaciones contextuales (FK Maquina desde Notificacion)
  └─→ MaquinaEliminada (backup histórico)

SISTEMA
  ├─→ CentroFormacion → AmbienteFormacion (1:N)
  ├─→ CentroFormacion → Ficha (1:N)
  └─→ Ficha → Usuario (N:1)
```

---

## 13. Seguridad y Validación

### 13.1 Hashing de Contraseñas

| Aspecto | Detalle |
|---------|---------|
| Algoritmo | PBKDF2-SHA256 |
| Iteraciones | 260.000 (Django 5.x default) |
| Almacenamiento | `DjangoUser.password` (no en modelo `Usuario`) |
| Formato | `pbkdf2_sha256$260000$<salt>$<hash>` |

### 13.2 Tokens de Recuperación

- `secrets.token_urlsafe(32)` → 43 caracteres Base64-URL-safe
- Expiración: **1 hora** desde solicitud
- **Uso único:** `token.usado = True` tras reset exitoso
- Campos de auditoría: `ip_solicitud`

### 13.3 Embeddings Faciales

- Almacenados como `JSONField` con lista de 128 floats
- **Nunca se almacenan imágenes de rostros**
- Comparación: similitud coseno normalizada, umbral configurable (default: 0.6)
- Rate limiting: 5 intentos/5 min/IP

### 13.4 Control de Acceso

| Mecanismo | Aplicación |
|-----------|-----------|
| `@login_required` | Todas las vistas protegidas |
| `UsuarioBackend` | Solo usuarios `activo` o `pendiente` pueden hacer login |
| `is_staff` | Basado en nombre del `TipoUsuario` |
| Permisos JSON | `TipoUsuario.permisos` verificados en cada vista |
| Nivel de acceso | `Documento.nivel_acceso` validado en cada consulta |

### 13.5 Protección CSRF

- `CsrfViewMiddleware` activo en toda la aplicación
- `@csrf_exempt` solo en endpoints de reconocimiento facial (pendiente en producción)
- Tokens CSRF en todos los formularios via `{% csrf_token %}`

### 13.6 Auditoría Completa

| Modelo | Registra |
|--------|---------|
| `SesionUsuario` | Cada login: IP, user-agent, timestamps |
| `IntentoReconocimientoFacial` | Todos los intentos faciales (éxito y fallo) |
| `LogActividad` | Cada acción significativa (crear, editar, eliminar) |
| `HistorialMaquina` | Cada cambio en el estado o datos de una máquina |
| `MaquinaEliminada` | Backup completo antes de cada eliminación |

---

## 14. Diagrama Entidad-Relación

```
TipoUsuario ─────────────────────────────┐
   │                                      │
   └─< Usuario (PK: id)                  │
         │ tipo_documento (ENUM)          │
         │ numero_documento (UNIQUE)      │
         │ estado (ENUM)                 │
         │ centro_formacion_id ──────────→ CentroFormacion
         │ ficha_id ─────────────────────→ Ficha (numero UNIQUE)
         │                                │
         ├─< SesionUsuario               │
         ├─< TokenRecuperacionPassword   │
         ├── ReconocimientoFacial (1:1)  │
         └─< IntentoReconocimientoFacial │

CategoriaMaquina ──────────────────────────────────────────┐
Proveedor ─────────────────────────────────────────────────│
   │                                                        │
   └─< Maquina (PK: id)                                    │
         │ codigo_inventario (UNIQUE)                       │
         │ numero_serie (UNIQUE)                            │
         │ estado (ENUM)                                    │
         │ responsable_id ───────────────────────→ Usuario  │
         │ created_by_id ────────────────────────→ Usuario  │
         │                                                   │
         ├─< AlertaMaquina ──→ resuelto_por: Usuario        │
         ├─< HistorialMaquina ──→ usuario: Usuario          │
         ├─< MantenimientoProgramado                        │
         │     ├─→ tecnico_asignado: Usuario                │
         │     ├─→ tecnico_realizado: Usuario               │
         │     └─M2M personal_adicional: Usuario            │
         ├─< UsoMaquinaria ──→ instructor: Usuario          │
         ├─< ObjetoMaquinaria                               │
         └─< Documento (maquina_relacionada, FK optional)   │
                                                            │
PiezaInventario ──→ maquina: Maquina (FK optional)         │
                ──→ responsable: Usuario (FK)               │

TipoDocumento ──┐                                          │
CategoriaDoc ───┤                                          │
                └─< Documento (PK: UUID)                   │
                      ├─→ creado_por: Usuario              │
                      ├─→ modificado_por: Usuario          │
                      └─M2M usuarios_acceso: Usuario        │

TipoReporte ────< Reporte (PK: UUID) ──→ usuario: Usuario  │
MetricasRendimiento ──→ categoria: CategoriaMaquina        │

Notificacion (PK: UUID) ──→ usuario: Usuario               │
                         ──→ maquina: Maquina (optional)   │
                         ──→ alerta: AlertaMaquina (opt.)  │
LogActividad (PK: UUID) ──→ usuario: Usuario               │
BackupDatabase (PK: UUID) ──→ creado_por: Usuario          │
Configuracion (clave UNIQUE) ─────────────────────────────┘
```

---

## 15. Flujo General de la Aplicación

```
USUARIO VISITA APLICACIÓN
        ↓
  ¿Autenticado?
   NO → /usuarios/login/
    │
    ├── Estándar (usuario + contraseña)
    │     → UsuarioBackend → SesionUsuario → dashboard
    │
    └── Facial (numero_doc + imagen)
          → DeepFace embed → similitud coseno → login

DASHBOARD (/usuarios/dashboard/)
  ├── Estadísticas: máquinas, alertas, mantenimientos
  ├── Eventos recientes del historial
  └── Máquinas asignadas al usuario

NAVEGACIÓN (según permisos TipoUsuario.permisos)
  │
  ├─ MAQUINARIA (/maquinaria/)
  │   ├── Lista + filtros → Detalle
  │   ├── Crear/Editar → HistorialMaquina automático
  │   ├── QR → generar_qr_maquina (PNG) → info_qr_maquina (escanear)
  │   ├── Alertas (crear, resolver)
  │   ├── Mantenimiento (programar, completar)
  │   └── Eliminar → MaquinaEliminada (backup JSON completo)
  │
  ├─ INVENTARIO (/inventario/)
  │   ├── Lista + filtros + alertas de vida útil
  │   ├── Nueva pieza (6 fotos angulares desde cámara)
  │   └── Editar / Eliminar
  │
  ├─ REPORTES (/reportes/)
  │   ├── Dashboard de reportes generados
  │   ├── Generar (tipo + filtros + formato)
  │   └── Descargar (PDF/Excel/CSV/JSON)
  │
  ├─ DOCUMENTOS (/documentos/)
  │   ├── Buscar (full-text en contenido_texto)
  │   ├── Subir (extrae contenido automáticamente)
  │   ├── Control de acceso (publico/interno/confidencial/restringido)
  │   └── Descargar
  │
  ├─ SISTEMA (/sistema/) — solo staff
  │   ├── Centro de control de usuarios (aprobar, crear, editar)
  │   ├── Backups (manual/automático cada 2h / restaurar)
  │   ├── Logs de actividad (filtros por módulo, nivel, usuario)
  │   └── Notificaciones
  │
  ├─ VISIÓN (/vision/)
  │   ├── Detectar maquinaria (POST imagen → TFLite → JSON)
  │   └── Estado del modelo
  │
  └─ API REST (/api/) — Token authentication
      ├── CRUD Maquinaria + Alertas (ViewSets)
      ├── Historial, cambio de estado, resolución de alertas
      ├── Generar y descargar reportes
      ├── Dashboard, métricas, estadísticas
      └── Importación/exportación masiva (Excel/CSV)

LOGOUT
  → SesionUsuario.activa = False
  → django.contrib.auth.logout()
  → Redirige a /usuarios/login/
```

---

## RESUMEN EJECUTIVO

El **Sistema de Gestión de Maquinaria Pesada SENA v2.0** es una aplicación web Django 5.2.6 empresarial con:

| Dimensión | Detalle |
|-----------|---------|
| **Módulos funcionales** | 8 apps Django independientes con ORM complejo |
| **Modelos de base de datos** | 25+ modelos con relaciones FK, M2M y UUID |
| **Autenticación** | Doble factor: contraseña (PBKDF2) + reconocimiento facial (DeepFace/Facenet) |
| **API REST** | 18+ endpoints DRF con autenticación por token |
| **Auditoría** | Logs completos de sesiones, acciones, cambios y eliminaciones |
| **IA integrada** | TFLite (detección de maquinaria) + DeepFace (reconocimiento facial) |
| **Reportes** | PDF (ReportLab), Excel (OpenPyXL), CSV, JSON |
| **Documentos** | Indexación full-text con PyMuPDF y python-docx |
| **Seguridad** | CSRF, rate limiting, hash PBKDF2, auditoría completa |
| **Backup** | Automático cada 2 horas (APScheduler) + manual desde UI |
| **Despliegue** | AWS Elastic Beanstalk ready (.ebextensions/django.config) |
| **Bootstrap** | v5.3.0 con archivos locales (sin dependencia de CDN) |
| **Bootstrap Icons** | v1.10.0 con fuentes locales (.woff2, .woff) |

---

*Informe Técnico generado el 23 de abril de 2026 — Sistema SENA Maquinaria v2.0*
