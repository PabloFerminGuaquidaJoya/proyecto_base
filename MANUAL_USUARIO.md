# Manual de Usuario
# Sistema SENA de Gestión de Maquinaria v2.0

---

## Tabla de Contenidos

1. [Introducción](#1-introducción)
2. [Requisitos del Sistema](#2-requisitos-del-sistema)
3. [Acceso al Sistema](#3-acceso-al-sistema)
   - 3.1 [Inicio de Sesión Tradicional](#31-inicio-de-sesión-tradicional)
   - 3.2 [Inicio de Sesión con Reconocimiento Facial](#32-inicio-de-sesión-con-reconocimiento-facial)
   - 3.3 [Recuperación de Contraseña](#33-recuperación-de-contraseña)
   - 3.4 [Registro de Nuevo Usuario](#34-registro-de-nuevo-usuario)
4. [Panel Principal (Dashboard)](#4-panel-principal-dashboard)
5. [Gestión de Usuarios](#5-gestión-de-usuarios)
   - 5.1 [Tipos de Usuario](#51-tipos-de-usuario)
   - 5.2 [Mi Perfil](#52-mi-perfil)
   - 5.3 [Configurar Reconocimiento Facial](#53-configurar-reconocimiento-facial)
6. [Gestión de Maquinaria](#6-gestión-de-maquinaria)
   - 6.1 [Dashboard de Maquinaria](#61-dashboard-de-maquinaria)
   - 6.2 [Registrar una Máquina](#62-registrar-una-máquina)
   - 6.3 [Consultar y Editar Máquinas](#63-consultar-y-editar-máquinas)
   - 6.4 [Estados de las Máquinas](#64-estados-de-las-máquinas)
   - 6.5 [Historial de Cambios](#65-historial-de-cambios)
   - 6.6 [Alertas](#66-alertas)
   - 6.7 [Mantenimiento](#67-mantenimiento)
   - 6.8 [Registro de Uso](#68-registro-de-uso)
   - 6.9 [Objetos del Equipo (Partes)](#69-objetos-del-equipo-partes)
7. [Gestión de Documentos](#7-gestión-de-documentos)
   - 7.1 [Repositorio de Documentos](#71-repositorio-de-documentos)
   - 7.2 [Subir un Documento](#72-subir-un-documento)
   - 7.3 [Buscar Documentos](#73-buscar-documentos)
   - 7.4 [Ver y Descargar Documentos](#74-ver-y-descargar-documentos)
   - 7.5 [Tipos y Categorías de Documentos](#75-tipos-y-categorías-de-documentos)
   - 7.6 [Niveles de Acceso](#76-niveles-de-acceso)
   - 7.7 [Control de Versiones](#77-control-de-versiones)
   - 7.8 [Estadísticas de Documentos](#78-estadísticas-de-documentos)
8. [Inventario de Piezas y Repuestos](#8-inventario-de-piezas-y-repuestos)
   - 8.1 [Consultar Inventario](#81-consultar-inventario)
   - 8.2 [Registrar Pieza](#82-registrar-pieza)
   - 8.3 [Estados de las Piezas](#83-estados-de-las-piezas)
9. [Reportes](#9-reportes)
   - 9.1 [Generar un Reporte](#91-generar-un-reporte)
   - 9.2 [Tipos de Reporte](#92-tipos-de-reporte)
   - 9.3 [Formatos de Exportación](#93-formatos-de-exportación)
   - 9.4 [Historial de Reportes](#94-historial-de-reportes)
10. [Configuración del Sistema](#10-configuración-del-sistema)
    - 10.1 [Parámetros Globales](#101-parámetros-globales)
    - 10.2 [Notificaciones](#102-notificaciones)
    - 10.3 [Respaldos Automáticos](#103-respaldos-automáticos)
    - 10.4 [Registros de Actividad (Logs)](#104-registros-de-actividad-logs)
11. [API REST](#11-api-rest)
12. [Panel de Administración Django](#12-panel-de-administración-django)
13. [Solución de Problemas Comunes](#13-solución-de-problemas-comunes)
14. [Glosario](#14-glosario)

---

## 1. Introducción

El **Sistema SENA de Gestión de Maquinaria v2.0** es una plataforma web diseñada para el control integral de maquinaria, documentos técnicos e inventarios en los centros de formación del SENA (Servicio Nacional de Aprendizaje de Colombia).

### Funcionalidades Principales

| Módulo | Descripción |
|---|---|
| Maquinaria | Registro, seguimiento y ciclo de vida completo de máquinas |
| Documentos | Repositorio centralizado de manuales y documentos técnicos |
| Inventario | Control de piezas, repuestos y componentes |
| Reportes | Generación de informes en PDF, Excel y CSV |
| Usuarios | Autenticación con contraseña o reconocimiento facial |
| Sistema | Configuración, notificaciones y respaldos automáticos |

### Tecnologías

- **Backend:** Django 5.2 con Python 3.8+
- **Frontend:** Bootstrap 5 + JavaScript
- **Base de datos:** MySQL / SQLite
- **Autenticación adicional:** OpenCV + MediaPipe (reconocimiento facial)

---

## 2. Requisitos del Sistema

### Para el Usuario Final (Navegador)

| Requisito | Mínimo |
|---|---|
| Navegador | Chrome 90+, Firefox 88+, Edge 90+, Safari 14+ |
| Conexión | Red local o Internet |
| Resolución | 1280 x 720 px o superior |
| Cámara web | Requerida solo para reconocimiento facial |

### Para el Administrador (Servidor)

| Componente | Versión Mínima |
|---|---|
| Python | 3.8+ |
| MySQL | 5.7+ (o SQLite para desarrollo) |
| RAM | 2 GB recomendados |
| Disco | 10 GB libres (más espacio para archivos subidos) |

---

## 3. Acceso al Sistema

### 3.1 Inicio de Sesión Tradicional

1. Abra el navegador y diríjase a la dirección del sistema (por ejemplo: `http://127.0.0.1:8000/`).
2. La pantalla de inicio de sesión se carga automáticamente.
3. Ingrese su **número de documento** o **correo electrónico** en el campo de usuario.
4. Ingrese su **contraseña**.
5. Haga clic en **"Iniciar Sesión"**.

> **Nota:** Si el sistema es nuevo, solicite al administrador la creación de su cuenta o utilice el enlace de registro.

### 3.2 Inicio de Sesión con Reconocimiento Facial

Si usted tiene registrado su perfil facial en el sistema:

1. En la pantalla de login, seleccione la opción **"Ingresar con Reconocimiento Facial"**.
2. Permita el acceso a la cámara cuando el navegador lo solicite.
3. Posicione su rostro frente a la cámara dentro del área indicada.
4. El sistema comparará su rostro con los perfiles registrados.
5. Si la similitud supera el 60%, el acceso se concederá automáticamente.

> **Limitaciones de seguridad:**
> - Máximo **5 intentos** cada 5 minutos por dirección IP.
> - Todos los intentos (exitosos y fallidos) quedan registrados en el log de auditoría.

### 3.3 Recuperación de Contraseña

1. En la pantalla de login, haga clic en **"¿Olvidó su contraseña?"**.
2. Ingrese su correo electrónico registrado.
3. Recibirá un correo con un enlace de recuperación (válido por **1 hora**).
4. Haga clic en el enlace del correo.
5. Ingrese y confirme su nueva contraseña.

**Requisitos de contraseña:**
- Mínimo 8 caracteres
- Al menos una letra mayúscula
- Al menos un número
- Al menos un carácter especial (!, @, #, etc.)

### 3.4 Registro de Nuevo Usuario

Si el administrador ha habilitado el registro público:

1. En la pantalla de login, haga clic en **"Registrarse"**.
2. Complete el formulario con:
   - Tipo y número de documento
   - Nombre completo
   - Correo electrónico
   - Contraseña (cumpliendo los requisitos)
3. Haga clic en **"Crear Cuenta"**.
4. El administrador deberá activar la cuenta antes de que pueda iniciar sesión.

---

## 4. Panel Principal (Dashboard)

Al iniciar sesión, se muestra el **Dashboard** con un resumen del estado general del sistema.

### Elementos del Dashboard

| Elemento | Descripción |
|---|---|
| Contadores superiores | Total de máquinas, documentos, alertas activas y reportes recientes |
| Gráfico de estados | Distribución visual de máquinas por estado operativo |
| Alertas recientes | Las últimas alertas sin resolver ordenadas por prioridad |
| Actividad reciente | Últimas acciones realizadas en el sistema |
| Accesos directos | Botones para las acciones más frecuentes |

### Navegación del Menú Lateral

El menú lateral (sidebar) contiene los accesos a todos los módulos:

1. Dashboard
2. Maquinaria
3. IA Assistant (Visión por computadora)
4. Reportes
5. Documentos
6. Mi Perfil
7. Manual de la App
8. Cerrar Sesión

---

## 5. Gestión de Usuarios

### 5.1 Tipos de Usuario

El sistema maneja los siguientes tipos de usuario con permisos diferenciados:

| Tipo | Descripción | Accesos Principales |
|---|---|---|
| Invitado | Acceso de solo lectura | Ver documentos públicos |
| Aprendiz | Usuario de formación | Consultar maquinaria y documentos asignados |
| Instructor | Personal docente | Registrar uso de maquinaria, crear documentos |
| Personal de Mantenimiento | Técnicos | Gestionar mantenimientos y alertas |
| Administrador | Control total | Acceso completo al sistema |

### 5.2 Mi Perfil

Para acceder y editar su perfil:

1. En el menú lateral, haga clic en **"Mi Perfil"**.
2. Podrá ver y editar:
   - Foto de perfil
   - Datos personales (nombre, documento, correo)
   - Especialidad y centro de formación
   - Configuración de notificaciones

**Para cambiar la foto de perfil:**
1. En Mi Perfil, haga clic en la foto actual o en el botón de cámara.
2. Seleccione una imagen desde su equipo (JPG, PNG).
3. Haga clic en **"Guardar"**.

### 5.3 Configurar Reconocimiento Facial

Para habilitar el inicio de sesión con reconocimiento facial:

1. Vaya a **Mi Perfil** → pestaña **"Reconocimiento Facial"**.
2. Haga clic en **"Registrar Rostro"**.
3. Permita el acceso a la cámara.
4. Posicione su rostro frente a la cámara con buena iluminación.
5. El sistema capturará y almacenará su perfil facial (solo un vector de 128 dimensiones, no la imagen).
6. Haga clic en **"Confirmar Registro"**.

> **Privacidad:** El sistema no almacena fotografías. Solo guarda un vector matemático (embedding) que representa su rostro. Este vector no puede revertirse a una imagen.

**Para eliminar el perfil facial:**
1. Vaya a **Mi Perfil** → **"Reconocimiento Facial"**.
2. Haga clic en **"Eliminar Perfil Facial"** y confirme.

---

## 6. Gestión de Maquinaria

### 6.1 Dashboard de Maquinaria

Acceda desde el menú lateral → **"Maquinaria"** → **"Dashboard"**.

Muestra:
- Conteo total de máquinas por estado
- Gráfico de distribución por categoría
- Alertas activas ordenadas por prioridad
- Mantenimientos programados próximos
- Últimas máquinas registradas o modificadas

### 6.2 Registrar una Máquina

1. Vaya a **Maquinaria** → **"Registrar Máquina"** (o botón "Nueva Máquina").
2. Complete el formulario con la siguiente información:

**Datos Básicos:**

| Campo | Descripción | Obligatorio |
|---|---|---|
| Nombre | Nombre descriptivo de la máquina | Sí |
| Código de inventario | Código único de identificación | Sí |
| Número de serie | Número de serie del fabricante | No |
| Marca | Fabricante o marca | Sí |
| Modelo | Modelo específico | No |
| Categoría | Categoría a la que pertenece | Sí |
| Estado | Estado operativo actual | Sí |
| Ubicación | Lugar físico donde se encuentra | Sí |
| Responsable | Usuario encargado de la máquina | No |

**Especificaciones Técnicas:**

| Campo | Descripción |
|---|---|
| Capacidad | Capacidad de trabajo (con unidad) |
| Potencia | Potencia del motor o sistema |
| Voltaje | Voltaje de operación |
| Dimensiones | Largo × Ancho × Alto |
| Peso | Peso total |

**Datos de Adquisición:**

| Campo | Descripción |
|---|---|
| Proveedor | Empresa proveedora |
| Fecha de compra | Fecha de adquisición |
| Valor | Costo de adquisición |
| Garantía hasta | Fecha de vencimiento de garantía |

3. Cargue imágenes de la máquina (opcional) usando el área de carga de fotos.
4. Haga clic en **"Guardar Máquina"**.

> **Nota:** Cada vez que se modifique la información de una máquina, el sistema registra automáticamente el cambio en el historial.

### 6.3 Consultar y Editar Máquinas

**Para listar todas las máquinas:**
1. Vaya a **Maquinaria** → **"Lista de Máquinas"**.
2. Use los filtros disponibles:
   - Por categoría
   - Por estado (disponible, en mantenimiento, fuera de servicio, etc.)
   - Por ubicación
   - Por texto libre (nombre, código, marca)
3. Haga clic en una máquina para ver su **detalle completo**.

**Para editar una máquina:**
1. En el detalle de la máquina, haga clic en **"Editar"**.
2. Modifique los campos necesarios.
3. Haga clic en **"Guardar Cambios"**.

**Para eliminar una máquina:**
1. En el detalle de la máquina, haga clic en **"Eliminar"**.
2. Confirme la acción.

> El sistema archiva las máquinas eliminadas con todo su historial en la tabla de máquinas eliminadas. No se pierde la información.

### 6.4 Estados de las Máquinas

| Estado | Descripción |
|---|---|
| Disponible | Operativa y lista para usar |
| Operativa | En uso actualmente |
| Mantenimiento Preventivo | En mantenimiento programado |
| En Reparación | Con falla, en proceso de reparación |
| Fuera de Servicio | No operativa temporalmente |
| Retirada | Dada de baja definitivamente |

### 6.5 Historial de Cambios

Cada máquina mantiene un registro automático de todos los cambios:

1. Abra el detalle de la máquina.
2. Vaya a la pestaña **"Historial"**.
3. Verá una lista cronológica con:
   - Fecha y hora del cambio
   - Usuario que realizó el cambio
   - Campo modificado
   - Valor anterior vs. nuevo valor

### 6.6 Alertas

El sistema genera y permite gestionar alertas asociadas a las máquinas.

**Tipos de Alerta:**

| Tipo | Descripción |
|---|---|
| Mantenimiento | Mantenimiento pendiente o vencido |
| Reparación | Requiere reparación urgente |
| Eficiencia | Rendimiento por debajo del umbral |
| Uso Excesivo | Horas de uso superan el límite |
| Garantía | Garantía próxima a vencer |
| Inspección | Inspección programada pendiente |

**Niveles de Prioridad:**

| Prioridad | Color |
|---|---|
| Baja | Azul / Verde |
| Media | Amarillo |
| Alta | Naranja |
| Crítica | Rojo |

**Para crear una alerta:**
1. En el detalle de la máquina, vaya a la pestaña **"Alertas"**.
2. Haga clic en **"Nueva Alerta"**.
3. Seleccione el tipo, prioridad y descripción.
4. Haga clic en **"Crear Alerta"**.

**Para resolver una alerta:**
1. En la lista de alertas, haga clic sobre la alerta.
2. Haga clic en **"Marcar como Resuelta"** e ingrese las observaciones.

### 6.7 Mantenimiento

**Para registrar un mantenimiento:**
1. En el detalle de la máquina, vaya a la pestaña **"Mantenimiento"**.
2. Haga clic en **"Programar Mantenimiento"**.
3. Complete el formulario:

| Campo | Descripción |
|---|---|
| Tipo | Preventivo, Correctivo, Predictivo, Urgente, Emergencia |
| Fecha programada | Cuándo se realizará |
| Técnico asignado | Responsable del mantenimiento |
| Duración estimada | Tiempo esperado (horas) |
| Descripción | Detalle del trabajo a realizar |
| Componentes | Lista de piezas o repuestos requeridos |
| Costo estimado | Presupuesto aproximado |

4. Haga clic en **"Guardar"**.

**Para completar un mantenimiento:**
1. Abra el registro de mantenimiento.
2. Haga clic en **"Registrar Finalización"**.
3. Ingrese:
   - Fecha y hora real de finalización
   - Duración real en horas
   - Costo real
   - Observaciones y resultados
4. Haga clic en **"Confirmar"**.

### 6.8 Registro de Uso

Para registrar el uso de una máquina en una sesión de formación:

1. En el detalle de la máquina, vaya a la pestaña **"Uso"**.
2. Haga clic en **"Registrar Uso"**.
3. Ingrese:
   - Instructor a cargo
   - Ficha o grupo de aprendices
   - Fecha y hora de inicio/fin
   - Horas de uso
   - Observaciones
4. Haga clic en **"Guardar"**.

### 6.9 Objetos del Equipo (Partes)

Para documentar partes o componentes específicos de una máquina:

1. En el detalle de la máquina, vaya a la pestaña **"Componentes"**.
2. Haga clic en **"Agregar Componente"**.
3. Puede agregar hasta **6 fotografías** del componente desde diferentes ángulos.
4. Complete la descripción y características del componente.
5. Haga clic en **"Guardar Componente"**.

---

## 7. Gestión de Documentos

El módulo de documentos es el **repositorio centralizado** para todos los archivos técnicos relacionados con la maquinaria y los procesos del centro de formación.

### 7.1 Repositorio de Documentos

Acceda desde el menú lateral → **"Documentos"**.

La vista principal muestra:
- Tarjetas o lista de documentos disponibles según su nivel de acceso
- Filtros por tipo, categoría, estado y fecha
- Barra de búsqueda rápida
- Estadísticas de uso

### 7.2 Subir un Documento

1. Vaya a **Documentos** → **"Subir Documento"**.
2. Complete el formulario:

**Información del Documento:**

| Campo | Descripción | Obligatorio |
|---|---|---|
| Título | Nombre descriptivo del documento | Sí |
| Tipo de documento | Categoría funcional del archivo | Sí |
| Categoría | Área temática | Sí |
| Descripción | Resumen del contenido | No |
| Archivo | Archivo a subir | Sí |
| Versión | Número de versión (ej. 1.0) | Sí |
| Nivel de acceso | Quién puede ver el documento | Sí |
| Fecha de expiración | Si el documento tiene vigencia limitada | No |
| Máquinas relacionadas | Vincular con máquinas del inventario | No |

**Formatos de archivo aceptados:**

| Formato | Extensión | Tamaño máximo |
|---|---|---|
| PDF | .pdf | 50 MB |
| Word | .docx | 50 MB |
| Excel | .xlsx | 50 MB |
| PowerPoint | .pptx | 50 MB |
| Texto plano | .txt | 10 MB |

3. Haga clic en **"Subir Documento"**.

> El sistema extrae automáticamente el texto del archivo (para PDF y Word) para habilitar la búsqueda de contenido completo.

### 7.3 Buscar Documentos

1. Vaya a **Documentos** → **"Buscar Documentos"**.
2. Use los filtros disponibles:

| Filtro | Descripción |
|---|---|
| Texto libre | Busca en título, descripción y contenido del archivo |
| Tipo de documento | Filtra por tipo funcional |
| Categoría | Filtra por área temática |
| Estado | Borrador, Publicado, Archivado, etc. |
| Nivel de acceso | Público, Interno, Confidencial |
| Fecha de creación | Rango de fechas |
| Máquina relacionada | Documentos vinculados a una máquina específica |

3. Los resultados se muestran con coincidencias resaltadas.
4. Haga clic en un resultado para ver el detalle.

### 7.4 Ver y Descargar Documentos

**Para ver un documento:**
1. Haga clic en el título del documento en la lista o resultados de búsqueda.
2. La página de detalle muestra:
   - Información completa del documento
   - Historial de versiones
   - Estadísticas de descargas y visualizaciones
   - Documentos relacionados

**Para descargar:**
1. En el detalle del documento, haga clic en **"Descargar"**.
2. El archivo se descargará a su equipo.

> La descarga queda registrada en las estadísticas del documento.

### 7.5 Tipos y Categorías de Documentos

**Tipos de Documento (8 tipos):**

| Tipo | Descripción |
|---|---|
| Manual | Manuales de operación y usuario |
| Guía de Mantenimiento | Procedimientos de mantenimiento |
| Ficha Técnica | Especificaciones técnicas del fabricante |
| Planos | Diagramas, esquemas y planos técnicos |
| Certificados | Certificaciones y acreditaciones |
| Procedimientos | Instructivos y protocolos de trabajo |
| Reportes | Informes y registros de actividad |
| Otro | Documentos que no encajan en las anteriores |

**Categorías (8 categorías):**
Organizadas por área temática con colores e íconos personalizados para identificación visual rápida.

### 7.6 Niveles de Acceso

| Nivel | Descripción | Quién puede ver |
|---|---|---|
| Público | Sin restricciones | Todos los usuarios, incluso invitados |
| Interno | Uso interno | Todos los usuarios con cuenta activa |
| Confidencial | Información sensible | Usuarios con permiso explícito |
| Restringido | Máxima restricción | Solo usuarios autorizados individualmente |

Para documentos Confidenciales y Restringidos, el administrador asigna los usuarios que tienen acceso desde el panel de administración.

### 7.7 Control de Versiones

Cuando se actualiza un documento:

1. Abra el documento que desea actualizar.
2. Haga clic en **"Subir Nueva Versión"**.
3. Seleccione el nuevo archivo.
4. Actualice la descripción del cambio y el número de versión.
5. Haga clic en **"Guardar"**.

El historial completo de versiones anteriores queda disponible en la pestaña **"Versiones"**.

**Ciclo de vida de un documento:**

```
Borrador → En Revisión → Aprobado → Publicado → Archivado → Obsoleto
```

### 7.8 Estadísticas de Documentos

Acceda a **Documentos** → **"Estadísticas"** para ver:
- Documentos más descargados
- Documentos más vistos
- Actividad por tipo y categoría
- Tendencias de uso en el tiempo
- Documentos próximos a vencer

---

## 8. Inventario de Piezas y Repuestos

### 8.1 Consultar Inventario

1. Vaya a **"Inventario"** en el menú.
2. La lista muestra todas las piezas registradas con:
   - Código de inventario
   - Nombre y descripción
   - Estado de la pieza
   - Cantidad disponible
   - Ubicación en bodega
   - Máquina a la que pertenece

Use los filtros para buscar por código, nombre, estado o ubicación.

### 8.2 Registrar Pieza

1. En la sección de inventario, haga clic en **"Registrar Pieza"**.
2. Complete el formulario:

| Campo | Descripción |
|---|---|
| Código de inventario | Identificador único de la pieza |
| Número de serie | Número de serie (si aplica) |
| Nombre | Nombre descriptivo de la pieza |
| Descripción | Características y uso |
| Estado | Estado actual de la pieza |
| Peso | Peso en kg o g |
| Dimensiones | Medidas físicas |
| Proveedor | Empresa proveedora |
| Fecha de adquisición | Cuándo fue comprada |
| Valor de adquisición | Costo |
| Ubicación en bodega | Pasillo, estante, posición |
| Horas de uso | Horas de uso acumuladas |
| Horas máximas | Límite de vida útil en horas |
| Responsable | Persona a cargo |
| Máquina asociada | Si pertenece a una máquina específica |

3. Haga clic en **"Guardar"**.

### 8.3 Estados de las Piezas

| Estado | Descripción |
|---|---|
| Nueva | Sin uso, en empaque original |
| Usada (buen estado) | Con uso pero funcional |
| Desgastada | Con desgaste visible, próxima a reemplazar |
| Dañada | Con falla o daño físico |
| Reparada | Fue dañada y se reparó |
| Obsoleta | Ya no compatible o fuera de uso |

---

## 9. Reportes

### 9.1 Generar un Reporte

1. Vaya a **"Reportes"** → **"Generar Reporte"**.
2. Seleccione el **tipo de reporte**.
3. Configure los **parámetros** según el tipo elegido:
   - Rango de fechas (inicio y fin)
   - Centro de formación
   - Categoría de maquinaria
   - Estado de las máquinas
   - Otros filtros específicos del reporte
4. Seleccione el **formato de salida** (PDF, Excel, CSV o JSON).
5. Haga clic en **"Generar Reporte"**.

> Los reportes grandes se generan en segundo plano. El sistema le notificará cuando estén listos.

### 9.2 Tipos de Reporte

| Tipo | Contenido |
|---|---|
| Inventario de Maquinaria | Estado completo de todas las máquinas |
| Mantenimientos | Registro de mantenimientos por período |
| Alertas | Alertas generadas y su estado de resolución |
| Uso de Maquinaria | Horas de uso por máquina y período |
| Documentos | Estadísticas del repositorio documental |
| Inventario de Piezas | Estado del inventario de repuestos |
| Actividad de Usuarios | Acciones realizadas por cada usuario |
| Resumen Ejecutivo | Vista consolidada para directivos |
| Personalizado | Reporte con campos seleccionados a medida |

### 9.3 Formatos de Exportación

| Formato | Mejor para |
|---|---|
| PDF | Impresión, presentaciones formales |
| Excel (.xlsx) | Análisis de datos, tablas dinámicas |
| CSV | Importación a otros sistemas |
| JSON | Integración con APIs o sistemas externos |

### 9.4 Historial de Reportes

1. Vaya a **"Reportes"** → **"Historial"**.
2. Verá la lista de todos los reportes generados con:
   - Tipo de reporte
   - Fecha y hora de generación
   - Usuario que lo solicitó
   - Estado (generando, completado, error)
   - Número de registros incluidos
3. Haga clic en **"Descargar"** para obtener un reporte ya generado.

---

## 10. Configuración del Sistema

> Esta sección es para **administradores del sistema**.

### 10.1 Parámetros Globales

1. Vaya a **"Sistema"** → **"Configuración"**.
2. La lista muestra todos los parámetros configurables.
3. Cada parámetro puede ser de tipo:
   - Texto
   - Número
   - Booleano (sí/no)
   - JSON (configuración compleja)
   - Fecha

**Para modificar un parámetro:**
1. Haga clic en el parámetro deseado.
2. Modifique el valor.
3. Haga clic en **"Guardar"**.

> Los parámetros marcados como "Solo Lectura" no pueden modificarse desde la interfaz (requieren cambio en el código).

### 10.2 Notificaciones

El sistema puede enviar notificaciones a los usuarios sobre eventos importantes.

**Tipos de Notificación:**

| Tipo | Uso |
|---|---|
| Informativa | Avisos generales del sistema |
| Éxito | Confirmación de operaciones |
| Advertencia | Situaciones que requieren atención |
| Error | Fallos o problemas detectados |
| Sistema | Eventos internos del sistema |

**Estados de Notificación:**
- Pendiente → Enviada → Leída → Archivada

**Para crear una notificación manual:**
1. Vaya a **"Sistema"** → **"Notificaciones"** → **"Nueva Notificación"**.
2. Seleccione el usuario(s) destinatario(s), tipo y mensaje.
3. Haga clic en **"Enviar"**.

### 10.3 Respaldos Automáticos

El sistema realiza respaldos automáticos cada **2 horas** mediante APScheduler. Los respaldos incluyen:
- Exportación de la base de datos en formato JSON
- Registro de la hora y estado del respaldo

**Para ver el historial de respaldos:**
1. Vaya a **"Sistema"** → **"Respaldos"**.
2. La lista muestra fecha, hora y estado de cada respaldo.

### 10.4 Registros de Actividad (Logs)

1. Vaya a **"Sistema"** → **"Logs"**.
2. Verá el registro de todas las acciones realizadas:
   - Quién hizo la acción
   - Qué acción realizó
   - Sobre qué objeto o módulo
   - Fecha y hora
   - Dirección IP

Use los filtros para buscar por usuario, tipo de acción o fecha.

---

## 11. API REST

El sistema expone una **API REST** para integración con otros sistemas o aplicaciones móviles.

### Autenticación

La API usa autenticación por token. Para obtener un token:

```
POST /api/auth/token/
{
  "username": "su_usuario",
  "password": "su_contraseña"
}
```

Incluya el token en todas las solicitudes:
```
Authorization: Token <su_token>
```

### Endpoints Principales

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/maquinaria/` | GET | Lista todas las máquinas (paginada, 50 por página) |
| `/api/maquinaria/` | POST | Crea una nueva máquina |
| `/api/maquinaria/{id}/` | GET | Detalle de una máquina |
| `/api/maquinaria/{id}/` | PUT/PATCH | Actualiza una máquina |
| `/api/maquinaria/{id}/` | DELETE | Elimina una máquina |
| `/api/alertas/` | GET | Lista alertas con filtros |
| `/api/alertas/` | POST | Crea una alerta |
| `/api/historial/` | GET | Historial de cambios (solo lectura) |

### Filtros Disponibles (Maquinaria)

| Parámetro | Descripción | Ejemplo |
|---|---|---|
| `categoria` | ID de categoría | `?categoria=2` |
| `estado` | Estado de la máquina | `?estado=disponible` |
| `ubicacion` | Texto en la ubicación | `?ubicacion=taller` |
| `search` | Búsqueda general | `?search=torno` |

### Ejemplo de Respuesta

```json
{
  "count": 42,
  "next": "http://servidor/api/maquinaria/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "nombre": "Torno CNC HAAS",
      "codigo_inventario": "MAQ-001",
      "estado": "disponible",
      "categoria": "Tornería",
      "ubicacion": "Taller Principal"
    }
  ]
}
```

### Visión por Computadora

| Endpoint | Método | Descripción |
|---|---|---|
| `/vision/api/detectar/` | POST | Envía una imagen para análisis de detección |
| `/vision/api/estado/` | GET | Verifica el estado del módulo de visión |

---

## 12. Panel de Administración Django

El panel de administración es una interfaz avanzada para gestión completa de la base de datos.

**Acceso:** `http://servidor/admin/` (requiere cuenta de superusuario)

### Secciones Disponibles

| Sección | Descripción |
|---|---|
| Usuarios | Crear, editar, activar y desactivar cuentas |
| Grupos y Permisos | Configurar roles y permisos detallados |
| Maquinaria | Administración completa de máquinas y categorías |
| Documentos | Gestión de documentos, tipos y categorías |
| Reportes | Configurar tipos de reporte disponibles |
| Sistema | Parámetros globales, notificaciones, centros de formación |
| Inventario | Gestión de piezas y repuestos |

### Crear un Superusuario

Desde la línea de comandos del servidor:
```bash
python manage.py createsuperuser
```

Siga las instrucciones para ingresar nombre de usuario, email y contraseña.

---

## 13. Solución de Problemas Comunes

### El sistema no carga o muestra error 500

**Causa posible:** El servidor Django no está corriendo o hay un error en la configuración.

**Solución:**
1. Verifique que el servidor esté activo.
2. Revise los logs del servidor en la consola donde se ejecutó `runserver`.
3. Contacte al administrador del sistema.

### No puedo iniciar sesión con mi contraseña correcta

**Causas posibles y soluciones:**
- La cuenta está inactiva → Contacte al administrador para que la active.
- El número de documento o correo es incorrecto → Verifique el dato ingresado.
- La contraseña tiene mayúsculas/minúsculas que no recuerda → Use la opción de recuperación de contraseña.

### El reconocimiento facial no funciona

**Causas posibles:**
- El navegador no tiene permiso para acceder a la cámara → Permita el acceso en la configuración del navegador.
- Iluminación insuficiente → Mejore la iluminación frente a la cámara.
- No tiene perfil facial registrado → Vaya a Mi Perfil y registre su rostro primero.
- Se superaron los 5 intentos → Espere 5 minutos antes de intentar nuevamente.

### No aparecen tipos de documento al subir un archivo

**Causa:** No se han cargado los datos iniciales del sistema.

**Solución (administrador):**
```bash
python scripts/poblacion/ejecutar_poblacion.py
```

### Error al subir documentos

**Causas posibles:**
- El archivo supera el tamaño máximo (50 MB para PDF/Word/Excel) → Comprima el archivo o divídalo.
- El formato no es compatible → Verifique la lista de formatos aceptados en la sección 7.2.
- La carpeta `media/` no existe → El administrador debe crearla en el servidor.

### Los reportes no se generan o quedan en estado "Pendiente"

**Causa probable:** El servicio de Celery (tareas en segundo plano) no está corriendo.

**Solución (administrador):**
```bash
celery -A app_prototipo worker --loglevel=info
```

### Error "No module named 'django'" al iniciar el servidor

**Causa:** El entorno virtual de Python no está activado.

**Solución:**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### La página muestra estilos rotos (sin CSS)

**Causa:** Los archivos estáticos no están recopilados o el servidor no los sirve correctamente.

**Solución (administrador):**
```bash
python manage.py collectstatic
```

---

## 14. Glosario

| Término | Definición |
|---|---|
| Aprendiz | Usuario del sistema que corresponde a un estudiante del SENA |
| Categoría | Clasificación temática de máquinas o documentos |
| Celery | Sistema de tareas en segundo plano para operaciones largas |
| Dashboard | Panel principal con resumen e indicadores del sistema |
| Embedding facial | Vector matemático de 128 dimensiones que representa un rostro |
| Ficha técnica | Documento con las especificaciones técnicas de una máquina |
| Historial | Registro cronológico de todos los cambios realizados a un registro |
| Instructor | Usuario del sistema que corresponde a un docente del SENA |
| Inventario | Conjunto de piezas, repuestos y componentes registrados |
| Mantenimiento correctivo | Intervención para reparar una falla ya ocurrida |
| Mantenimiento preventivo | Intervención programada para evitar fallas futuras |
| Mantenimiento predictivo | Intervención basada en indicadores de desgaste o uso |
| MediaPipe | Librería de Google para procesamiento de imágenes y video |
| MySQL | Sistema de gestión de base de datos relacional |
| PDF | Formato de documento portátil (Portable Document Format) |
| Redis | Sistema de caché en memoria usado para sesiones y colas de tareas |
| Reporte | Documento generado automáticamente con datos del sistema |
| REST API | Interfaz de programación que permite la integración con sistemas externos |
| SQLite | Base de datos ligera usada en desarrollo local |
| Superusuario | Cuenta con acceso total al sistema incluyendo el panel de administración |
| Token | Clave única para autenticación en la API REST |
| Versión (documento) | Número que identifica una revisión específica de un documento |

---

*Manual de Usuario — Sistema SENA de Gestión de Maquinaria v2.0*
*Última actualización: Abril 2026*
