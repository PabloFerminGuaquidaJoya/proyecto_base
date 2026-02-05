# Módulo de Reconocimiento Facial - Guía de Instalación y Uso

## Resumen

Se ha implementado un sistema completo de reconocimiento facial **opcional** para el login del sistema SENA. Los usuarios pueden elegir entre:
- Iniciar sesión con contraseña (método tradicional)
- Iniciar sesión con reconocimiento facial (nuevo método)

**Características principales:**
- Usa OpenCV + MediaPipe (solución ligera de Google)
- Almacena solo embeddings faciales (vectores numéricos de 128 dimensiones)
- NO almacena imágenes faciales completas (privacidad)
- Umbral de similitud: 60% para autenticación
- Rate limiting: máximo 5 intentos por IP cada 5 minutos
- Auditoría completa de todos los intentos

---

## Paso 1: Instalar Dependencias

Debes activar tu entorno virtual y luego instalar las nuevas dependencias:

### En Windows:

```bash
# Navegar al directorio del proyecto
cd c:\Users\Asus\OneDrive\Escritorio\proyecto_base\myworld

# Activar entorno virtual
venv\Scripts\activate

# Instalar dependencias nuevas
pip install opencv-python==4.8.1.78 opencv-contrib-python==4.8.1.78 mediapipe==0.10.9 numpy==1.24.3
```

**Nota:** La instalación de OpenCV y MediaPipe puede tardar varios minutos.

---

## Paso 2: Ejecutar Migraciones de Base de Datos

Una vez instaladas las dependencias, debes crear y aplicar las migraciones para los nuevos modelos:

```bash
# Asegúrate de estar en el directorio correcto
cd app_prototipo

# Crear migraciones
python manage.py makemigrations usuarios

# Aplicar migraciones
python manage.py migrate
```

**Resultado esperado:**
```
Migrations for 'usuarios':
  usuarios\migrations\0003_reconocimientofacial_intentoreconocimientofacial.py
    - Create model ReconocimientoFacial
    - Create model IntentoReconocimientoFacial

Running migrations:
  Applying usuarios.0003_reconocimientofacial_intentoreconocimientofacial... OK
```

---

## Paso 3: Iniciar el Servidor

```bash
python manage.py runserver
```

Abre tu navegador en: **http://127.0.0.1:8000/usuarios/login/**

---

## Cómo Usar el Reconocimiento Facial

### A. Primera vez - Registrar Rostro

**Opción 1: Desde el Perfil** (Recomendado)

1. Inicia sesión con tu contraseña
2. Ve a tu perfil: http://127.0.0.1:8000/usuarios/perfil/
3. Busca la sección "Reconocimiento Facial" (pendiente de agregar UI)
4. Haz clic en "Registrar Rostro"
5. Permite el acceso a la cámara
6. Centra tu rostro en el marco verde
7. Haz clic en "Capturar"
8. Confirma el registro

**Opción 2: Mediante API** (Para testing)

Puedes usar el siguiente JavaScript en la consola del navegador (estando autenticado):

```javascript
// 1. Abre la página de perfil
// 2. Abre la consola (F12)
// 3. Ejecuta este código adaptándolo a tu caso

// Esta función captura desde la cámara y registra el rostro
async function registrarRostroTest() {
    try {
        // Solicitar acceso a la cámara
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { width: 640, height: 480, facingMode: 'user' }
        });

        // Crear elementos para captura
        const video = document.createElement('video');
        video.srcObject = stream;
        video.play();

        // Esperar a que el video esté listo
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Capturar frame
        const canvas = document.createElement('canvas');
        canvas.width = 640;
        canvas.height = 480;
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0);
        const imagenBase64 = canvas.toDataURL('image/jpeg', 0.8);

        // Detener cámara
        stream.getTracks().forEach(track => track.stop());

        // Enviar al backend
        const response = await fetch('/usuarios/api/registrar-rostro/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ imagen: imagenBase64 })
        });

        const data = await response.json();
        console.log('Resultado:', data);
        alert(data.success ? 'Rostro registrado!' : 'Error: ' + data.error);
    } catch (error) {
        console.error('Error:', error);
        alert('Error: ' + error.message);
    }
}

// Ejecutar
registrarRostroTest();
```

### B. Login con Reconocimiento Facial

1. Ve a la página de login: http://127.0.0.1:8000/usuarios/login/
2. Haz clic en el botón **"Iniciar con Reconocimiento Facial"**
3. Se abre un modal
4. Ingresa tu número de documento
5. Haz clic en **"Continuar"**
6. Permite el acceso a la cámara cuando el navegador lo solicite
7. Centra tu rostro en el marco verde animado
8. Haz clic en **"Capturar y Autenticar"**
9. El sistema:
   - Captura tu rostro
   - Extrae el embedding facial
   - Lo compara con el embedding almacenado
   - Si la similitud es ≥ 60%, te autentica automáticamente
10. Si es exitoso, serás redirigido al dashboard

### C. Posibles Errores y Soluciones

#### Error: "No se pudo acceder a la cámara"
**Solución:**
- Verifica que tu navegador tenga permisos para usar la cámara
- En Chrome: Settings → Privacy and Security → Site Settings → Camera
- Asegúrate de que no haya otra aplicación usando la cámara

#### Error: "No se detectó ningún rostro"
**Solución:**
- Asegúrate de estar frente a la cámara
- Mejora la iluminación
- Acércate más a la cámara

#### Error: "Se detectaron múltiples rostros"
**Solución:**
- Asegúrate de que solo tú estés en el cuadro de la cámara

#### Error: "Imagen muy oscura"
**Solución:**
- Aumenta la iluminación de la habitación
- Enciende luces adicionales

#### Error: "Imagen desenfocada"
**Solución:**
- Mantén la cámara estable
- Asegúrate de que la cámara esté enfocada

#### Error: "Rostro no coincide"
**Solución:**
- Intenta desde el mismo ángulo/posición que cuando registraste tu rostro
- Si persiste, vuelve a registrar tu rostro desde el perfil

#### Error: "Demasiados intentos"
**Solución:**
- Has excedido los 5 intentos permitidos
- Espera 5 minutos antes de intentar nuevamente
- O usa login con contraseña

---

## Verificar en el Admin

Puedes verificar que todo funciona correctamente desde el panel de administración:

1. Ve a: http://127.0.0.1:8000/admin/
2. Login con tu superusuario
3. Busca las nuevas secciones:
   - **Reconocimientos Faciales**: Ver usuarios con reconocimiento facial registrado
   - **Intentos de Reconocimiento Facial**: Ver todos los intentos (exitosos y fallidos)

**Campos importantes:**
- **ReconocimientoFacial:**
  - `usuario`: Usuario asociado
  - `activo`: Si el reconocimiento está activo
  - `confianza_registro`: Nivel de confianza del registro
  - `fecha_registro`: Cuándo se registró
  - `ip_registro`: Desde qué IP se registró

- **IntentoReconocimientoFacial:**
  - `usuario`: Usuario que intentó
  - `tipo_intento`: registro / login / actualizacion
  - `resultado`: exitoso / fallido / error
  - `similitud`: Nivel de similitud calculado (0-1)
  - `fecha_intento`: Cuándo ocurrió
  - `mensaje_error`: Descripción del error si falló

---

## Arquitectura Técnica

### Archivos Modificados/Creados

1. **requirements.txt** - Nuevas dependencias
2. **usuarios/facial_recognition.py** - Módulo core (NUEVO)
3. **usuarios/models.py** - Modelos ReconocimientoFacial e IntentoReconocimientoFacial
4. **usuarios/views.py** - 4 nuevas vistas API
5. **usuarios/urls.py** - 4 nuevas rutas
6. **usuarios/admin.py** - Registro de nuevos modelos
7. **usuarios/templates/usuarios/modern_login.html** - Modal + JavaScript

### Flujo de Autenticación Facial

```
1. Usuario → Clic "Iniciar con Reconocimiento Facial"
2. Ingresa número de documento
3. Sistema solicita acceso a cámara
4. Usuario captura rostro
5. Frontend:
   - Captura frame del video
   - Convierte a base64 JPEG
   - POST a /usuarios/api/login-facial/
6. Backend (facial_service):
   - Decodifica imagen base64 → numpy array
   - Valida calidad (brillo, enfoque, resolución)
   - Detecta rostro con MediaPipe Face Detection
   - Extrae embedding de 128 dimensiones con MediaPipe Face Mesh
   - Compara con embedding almacenado (similitud coseno)
   - Si similitud ≥ 60% → AUTENTICADO
7. Si exitoso:
   - Crea sesión Django (login())
   - Registra en SesionUsuario
   - Actualiza ultimo_acceso
   - Redirige a dashboard
8. Si falla:
   - Registra intento fallido en IntentoReconocimientoFacial
   - Muestra error al usuario
```

### Embeddings Faciales

**¿Qué son los embeddings?**
- Vectores numéricos de 128 dimensiones que representan características únicas de un rostro
- Se calculan usando MediaPipe Face Mesh (468 landmarks faciales)
- Se seleccionan 60 puntos clave estratégicos (ojos, nariz, boca, cejas, contorno)
- Se calculan características geométricas (distancias, proporciones)
- Se reduce a 128 dimensiones mediante agregación estadística

**¿Por qué embeddings y no imágenes?**
- **Privacidad**: No se puede reconstruir la imagen del rostro desde el embedding
- **Eficiencia**: 128 números ocupan mucho menos espacio que una imagen
- **Velocidad**: Comparar embeddings es más rápido que comparar imágenes
- **GDPR compliant**: Cumple con regulaciones de privacidad de datos

### Seguridad

1. **Rate Limiting**: Máximo 5 intentos por IP cada 5 minutos (Django cache)
2. **Validación de calidad**: Brillo, enfoque, resolución
3. **Detección única**: Solo procesa si hay exactamente 1 rostro
4. **Auditoría completa**: Todos los intentos se registran con IP, user-agent, similitud
5. **Verificación de estado**: Solo usuarios activos pueden autenticarse
6. **Sin almacenamiento de imágenes**: Solo embeddings numéricos

---

## Testing del Sistema

### Test 1: Registro de Rostro
```bash
# 1. Login con usuario existente
# 2. Ejecutar código JavaScript de registrarRostroTest() en consola
# 3. Verificar en admin que se creó registro en ReconocimientoFacial
```

### Test 2: Login Facial Exitoso
```bash
# 1. Ir a /usuarios/login/
# 2. Clic "Iniciar con Reconocimiento Facial"
# 3. Ingresar documento de usuario con rostro registrado
# 4. Capturar rostro
# 5. Verificar autenticación exitosa
# 6. Verificar redirección a dashboard
# 7. Verificar en admin: IntentoReconocimientoFacial con resultado='exitoso'
```

### Test 3: Login Facial Fallido
```bash
# 1. Ir a /usuarios/login/
# 2. Clic "Iniciar con Reconocimiento Facial"
# 3. Ingresar documento de usuario A
# 4. Capturar rostro de usuario B (diferente)
# 5. Verificar error "Rostro no coincide"
# 6. Verificar en admin: IntentoReconocimientoFacial con resultado='fallido'
```

### Test 4: Rate Limiting
```bash
# 1. Intentar login facial 6 veces seguidas con datos incorrectos
# 2. En el 6to intento verificar mensaje de rate limiting
# 3. Esperar 5 minutos
# 4. Verificar que se puede intentar nuevamente
```

---

## Solución de Problemas

### Problema: "ModuleNotFoundError: No module named 'cv2'"
**Solución:**
```bash
pip install opencv-python opencv-contrib-python
```

### Problema: "ModuleNotFoundError: No module named 'mediapipe'"
**Solución:**
```bash
pip install mediapipe
```

### Problema: Error de migración
**Solución:**
```bash
python manage.py migrate --run-syncdb
```

### Problema: No se crea la tabla en MySQL
**Solución:**
```bash
# Verificar que la base de datos esté activa
python manage.py showmigrations usuarios

# Si no aparecen las nuevas migraciones:
python manage.py makemigrations usuarios --empty
# Editar el archivo generado y agregar las operaciones manualmente
python manage.py migrate
```

---

## Próximas Mejoras (Fase 2)

1. **Liveness Detection**: Detectar fotos vs rostro real (parpadeo, movimiento de cabeza)
2. **UI en Perfil**: Agregar sección visual en el perfil para registrar/eliminar rostro
3. **Múltiples ángulos**: Capturar 3-5 fotos desde diferentes ángulos para mejor precisión
4. **Re-entrenamiento automático**: Actualizar embedding cada 6 meses
5. **2FA opcional**: Reconocimiento facial + PIN/contraseña como doble factor
6. **Dashboard de analytics**: Estadísticas de uso, tasa de éxito, intentos fallidos
7. **Notificaciones**: Alertar al usuario cuando alguien intenta autenticarse con su rostro

---

## Soporte

Si encuentras problemas o necesitas ayuda:
1. Revisa esta guía completamente
2. Verifica los logs en la consola del navegador (F12)
3. Verifica los logs del servidor Django
4. Revisa el admin de Django para ver los intentos registrados
5. Consulta el plan de implementación en: `C:\Users\Asus\.claude\plans\sunny-marinating-sunrise.md`

---

**Desarrollado con:** OpenCV 4.8.1 + MediaPipe 0.10.9
**Framework:** Django 5.2.7
**Fecha:** Enero 2026
