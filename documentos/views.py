from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, FileResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.files.storage import default_storage
from django.db.models import Q, Count, Sum
import json
import hashlib
from .models import Documento, TipoDocumento, CategoriaDocumento
from .forms import (
    DocumentoForm, TipoDocumentoForm, CategoriaDocumentoForm,
    BuscarDocumentosForm, SubirDocumentoRapidoForm, GestionarPermisosForm,
    ComentarioDocumentoForm, ImportarDocumentosForm, NuevaVersionForm,
    FiltroMisDocumentosForm, ConfiguracionDocumentosForm
)
from maquinaria.models import Maquina
from usuarios.models import Usuario

@login_required
def repositorio_view(request):
    """Vista principal del repositorio de documentos"""
    documentos = Documento.objects.select_related(
        'tipo_documento', 'categoria', 'creado_por', 'maquina_relacionada'
    ).all()

    # Aplicar filtros si existen
    categoria_id = request.GET.get('categoria')
    tipo_id = request.GET.get('tipo')
    estado = request.GET.get('estado')
    query = request.GET.get('q')

    if categoria_id:
        documentos = documentos.filter(categoria_id=categoria_id)
    if tipo_id:
        documentos = documentos.filter(tipo_documento_id=tipo_id)
    if estado:
        documentos = documentos.filter(estado=estado)
    if query:
        documentos = documentos.filter(
            Q(titulo__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(palabras_clave__icontains=query) |
            Q(contenido_texto__icontains=query)
        )

    # Paginación
    paginator = Paginator(documentos, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Datos para filtros
    categorias = CategoriaDocumento.objects.filter(activo=True)
    tipos = TipoDocumento.objects.filter(activo=True)

    # Estadísticas
    stats = {
        'total_documentos': Documento.objects.count(),
        'documentos_mes': Documento.objects.filter(
            fecha_creacion__gte=timezone.now().replace(day=1)
        ).count(),
        'categorias_activas': categorias.count(),
        'tipos_activos': tipos.count(),
    }

    context = {
        'title': 'Repositorio de Documentos',
        'documentos': page_obj,
        'categorias': categorias,
        'tipos': tipos,
        'estados': Documento.ESTADO_CHOICES,
        'stats': stats,
        'query': query,
        'total_documentos': stats['total_documentos'],
        'manuales_recientes': page_obj,
    }
    return render(request, 'documentos/modern_repositorio.html', context)

@login_required
def buscar_documentos_view(request):
    """Vista para búsqueda avanzada de documentos"""
    form = BuscarDocumentosForm(request.GET or None)
    documentos = Documento.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get('query')
        categoria = form.cleaned_data.get('categoria')
        tipo_documento = form.cleaned_data.get('tipo_documento')
        estado = form.cleaned_data.get('estado')
        nivel_acceso = form.cleaned_data.get('nivel_acceso')
        maquina = form.cleaned_data.get('maquina_relacionada')
        fecha_inicio = form.cleaned_data.get('fecha_inicio')
        fecha_fin = form.cleaned_data.get('fecha_fin')

        if query:
            documentos = documentos.filter(
                Q(titulo__icontains=query) |
                Q(descripcion__icontains=query) |
                Q(contenido_texto__icontains=query)
            )
        if categoria:
            documentos = documentos.filter(categoria=categoria)
        if tipo_documento:
            documentos = documentos.filter(tipo_documento=tipo_documento)
        if estado:
            documentos = documentos.filter(estado=estado)
        if nivel_acceso:
            documentos = documentos.filter(nivel_acceso=nivel_acceso)
        if maquina:
            documentos = documentos.filter(maquina_relacionada=maquina)
        if fecha_inicio:
            documentos = documentos.filter(fecha_creacion__gte=fecha_inicio)
        if fecha_fin:
            documentos = documentos.filter(fecha_creacion__lte=fecha_fin)

    paginator = Paginator(documentos, 20)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        'title': 'Buscar Documentos',
        'form': form,
        'documentos': page_obj,
        'total_resultados': documentos.count(),
    }
    return render(request, 'documentos/buscar_documentos.html', context)

@login_required
def subir_documento_view(request):
    """Vista para subir un nuevo documento"""
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            # Obtener el usuario actual usando numero_documento
            try:
                usuario = Usuario.objects.get(numero_documento=request.user.username)
                documento.creado_por = usuario
            except Usuario.DoesNotExist:
                messages.error(request, 'Error: Tu perfil de usuario no está completo. Contacta al administrador.')
                return redirect('documentos:repositorio')

            # Calcular checksum del archivo
            if documento.archivo:
                archivo_content = documento.archivo.read()
                documento.checksum = hashlib.sha256(archivo_content).hexdigest()
                documento.archivo.seek(0)  # Resetear puntero

            documento.save()
            form.save_m2m()  # Guardar relaciones many-to-many

            messages.success(request, f'Documento "{documento.titulo}" subido exitosamente.')
            return redirect('documentos:detalle_documento', pk=documento.pk)
        else:
            messages.error(request, 'Error al subir el documento. Por favor revisa los campos.')
    else:
        form = DocumentoForm()

    context = {
        'title': 'Subir Documento',
        'form': form,
    }
    return render(request, 'documentos/subir_documento.html', context)

@login_required
def detalle_documento_view(request, pk):
    """Vista de detalle de un documento"""
    documento = get_object_or_404(
        Documento.objects.select_related('tipo_documento', 'categoria', 'creado_por', 'modificado_por', 'maquina_relacionada'),
        pk=pk
    )

    # Incrementar contador de visualizaciones
    documento.total_visualizaciones += 1
    documento.save(update_fields=['total_visualizaciones'])

    context = {
        'title': f'Documento: {documento.titulo}',
        'documento': documento,
    }
    return render(request, 'documentos/detalle_documento.html', context)

@login_required
def editar_documento_view(request, pk):
    """Vista para editar un documento existente"""
    documento = get_object_or_404(Documento, pk=pk)

    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES, instance=documento)
        if form.is_valid():
            documento = form.save(commit=False)
            try:
                usuario = Usuario.objects.get(numero_documento=request.user.username)
                documento.modificado_por = usuario
            except Usuario.DoesNotExist:
                pass
            documento.save()
            form.save_m2m()

            messages.success(request, f'Documento "{documento.titulo}" actualizado exitosamente.')
            return redirect('documentos:detalle_documento', pk=documento.pk)
        else:
            messages.error(request, 'Error al actualizar el documento.')
    else:
        form = DocumentoForm(instance=documento)

    context = {
        'title': f'Editar: {documento.titulo}',
        'form': form,
        'documento': documento,
    }
    return render(request, 'documentos/editar_documento.html', context)

@login_required
def eliminar_documento_view(request, pk):
    """Vista para eliminar un documento"""
    documento = get_object_or_404(Documento, pk=pk)

    if request.method == 'POST':
        titulo = documento.titulo
        # Eliminar archivo físico
        if documento.archivo:
            try:
                documento.archivo.delete()
            except:
                pass
        documento.delete()
        messages.success(request, f'Documento "{titulo}" eliminado exitosamente.')
        return redirect('documentos:repositorio')

    context = {
        'title': f'Eliminar: {documento.titulo}',
        'documento': documento,
    }
    return render(request, 'documentos/eliminar_documento.html', context)

@login_required
def descargar_documento(request, pk):
    """Descargar un documento"""
    documento = get_object_or_404(Documento, pk=pk)

    # Incrementar contador de descargas
    documento.total_descargas += 1
    documento.ultima_descarga = timezone.now()
    documento.save(update_fields=['total_descargas', 'ultima_descarga'])

    # Servir archivo
    try:
        response = FileResponse(documento.archivo.open('rb'), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{documento.archivo.name}"'
        return response
    except Exception as e:
        messages.error(request, f'Error al descargar el documento: {str(e)}')
        return redirect('documentos:detalle_documento', pk=pk)

@login_required
def preview_documento_view(request, pk):
    """Vista previa del documento"""
    documento = get_object_or_404(Documento, pk=pk)

    context = {
        'title': f'Vista Previa: {documento.titulo}',
        'documento': documento,
    }
    return render(request, 'documentos/preview_documento.html', context)

@login_required
def ver_documento_view(request, pk):
    """Vista para ver el documento en el navegador"""
    documento = get_object_or_404(Documento, pk=pk)

    # Incrementar visualizaciones
    documento.total_visualizaciones += 1
    documento.save(update_fields=['total_visualizaciones'])

    context = {
        'title': f'Ver: {documento.titulo}',
        'documento': documento,
    }
    return render(request, 'documentos/ver_documento.html', context)

@login_required
def versiones_documento_view(request, pk):
    """Vista para ver versiones del documento"""
    documento = get_object_or_404(Documento, pk=pk)

    # En una implementación completa, aquí habría un modelo VersionDocumento
    versiones = []  # Placeholder

    context = {
        'title': f'Versiones: {documento.titulo}',
        'documento': documento,
        'versiones': versiones,
    }
    return render(request, 'documentos/versiones_documento.html', context)

@login_required
@require_http_methods(["POST"])
def nueva_version_documento(request, pk):
    """Crear nueva versión de un documento"""
    documento = get_object_or_404(Documento, pk=pk)
    form = NuevaVersionForm(request.POST, request.FILES)

    if form.is_valid():
        # Aquí se crearía una nueva versión
        # Por ahora solo actualizamos el número de versión
        documento.version = form.cleaned_data['numero_version']
        try:
            usuario = Usuario.objects.get(numero_documento=request.user.username)
            documento.modificado_por = usuario
        except Usuario.DoesNotExist:
            pass
        documento.save()

        messages.success(request, f'Nueva versión {documento.version} creada exitosamente.')
        return JsonResponse({'success': True, 'version': documento.version})

    return JsonResponse({'success': False, 'errors': form.errors}, status=400)

@login_required
def comparar_versiones_view(request, pk):
    """Comparar versiones de documentos"""
    documento = get_object_or_404(Documento, pk=pk)

    context = {
        'title': f'Comparar Versiones: {documento.titulo}',
        'documento': documento,
    }
    return render(request, 'documentos/comparar_versiones.html', context)

@login_required
def categorias_documentos_view(request):
    """Vista de gestión de categorías"""
    categorias = CategoriaDocumento.objects.annotate(
        num_documentos=Count('documento')
    ).order_by('orden', 'nombre')

    context = {
        'title': 'Categorías de Documentos',
        'categorias': categorias,
    }
    return render(request, 'documentos/categorias_documentos.html', context)

@login_required
def crear_categoria_documento_view(request):
    """Crear nueva categoría de documento"""
    if request.method == 'POST':
        form = CategoriaDocumentoForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" creada exitosamente.')
            return redirect('documentos:categorias_documentos')
    else:
        form = CategoriaDocumentoForm()

    context = {
        'title': 'Crear Categoría',
        'form': form,
    }
    return render(request, 'documentos/crear_categoria_documento.html', context)

@login_required
def tipos_documento_view(request):
    """Vista de gestión de tipos de documento"""
    tipos = TipoDocumento.objects.annotate(
        num_documentos=Count('documento')
    ).order_by('nombre')

    context = {
        'title': 'Tipos de Documento',
        'tipos': tipos,
    }
    return render(request, 'documentos/tipos_documento.html', context)

@login_required
def crear_tipo_documento_view(request):
    """Crear nuevo tipo de documento"""
    if request.method == 'POST':
        form = TipoDocumentoForm(request.POST)
        if form.is_valid():
            tipo = form.save()
            messages.success(request, f'Tipo "{tipo.nombre}" creado exitosamente.')
            return redirect('documentos:tipos_documento')
    else:
        form = TipoDocumentoForm()

    context = {
        'title': 'Crear Tipo de Documento',
        'form': form,
    }
    return render(request, 'documentos/crear_tipo_documento.html', context)

@login_required
def documentos_por_categoria_view(request, categoria_id):
    """Documentos filtrados por categoría"""
    categoria = get_object_or_404(CategoriaDocumento, pk=categoria_id)
    documentos = Documento.objects.filter(categoria=categoria).select_related(
        'tipo_documento', 'creado_por'
    )

    paginator = Paginator(documentos, 20)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        'title': f'Documentos: {categoria.nombre}',
        'categoria': categoria,
        'documentos': page_obj,
    }
    return render(request, 'documentos/documentos_por_categoria.html', context)

@login_required
def documentos_por_tipo_view(request, tipo_id):
    """Documentos filtrados por tipo"""
    tipo = get_object_or_404(TipoDocumento, pk=tipo_id)
    documentos = Documento.objects.filter(tipo_documento=tipo).select_related(
        'categoria', 'creado_por'
    )

    paginator = Paginator(documentos, 20)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        'title': f'Documentos: {tipo.nombre}',
        'tipo': tipo,
        'documentos': page_obj,
    }
    return render(request, 'documentos/documentos_por_tipo.html', context)

@login_required
def documentos_maquina_view(request, maquina_id):
    """Documentos de una máquina específica"""
    maquina = get_object_or_404(Maquina, pk=maquina_id)
    documentos = Documento.objects.filter(maquina_relacionada=maquina).select_related(
        'tipo_documento', 'categoria', 'creado_por'
    )

    # Filtrar por tipo si se especifica
    tipo_filtro = request.GET.get('tipo')
    if tipo_filtro:
        documentos = documentos.filter(tipo_documento_id=tipo_filtro)

    # Estadísticas
    tipos_disponibles = TipoDocumento.objects.filter(
        documento__maquina_relacionada=maquina
    ).distinct()
    tipos_count = tipos_disponibles.count()
    total_descargas = documentos.aggregate(Sum('total_descargas'))['total_descargas__sum'] or 0

    paginator = Paginator(documentos, 20)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        'title': f'Documentos: {maquina.nombre}',
        'maquina': maquina,
        'documentos': page_obj,
        'tipos_disponibles': tipos_disponibles,
        'tipos_count': tipos_count,
        'total_descargas': total_descargas,
    }
    return render(request, 'documentos/documentos_maquina.html', context)

@login_required
def gestionar_permisos_view(request, pk):
    """Gestionar permisos de acceso a documento"""
    documento = get_object_or_404(Documento, pk=pk)

    if request.method == 'POST':
        form = GestionarPermisosForm(request.POST)
        if form.is_valid():
            documento.nivel_acceso = form.cleaned_data['nivel_acceso']
            documento.save()

            # Actualizar usuarios con acceso
            documento.usuarios_acceso.set(form.cleaned_data['usuarios_con_acceso'])

            messages.success(request, 'Permisos actualizados exitosamente.')
            return redirect('documentos:detalle_documento', pk=pk)
    else:
        form = GestionarPermisosForm(initial={
            'nivel_acceso': documento.nivel_acceso,
        })
        form.fields['usuarios_con_acceso'].initial = documento.usuarios_acceso.all()

    context = {
        'title': f'Gestionar Permisos: {documento.titulo}',
        'documento': documento,
        'form': form,
    }
    return render(request, 'documentos/gestionar_permisos.html', context)

@login_required
@require_http_methods(["POST"])
def solicitar_acceso_documento(request, pk):
    """Solicitar acceso a un documento"""
    documento = get_object_or_404(Documento, pk=pk)

    # Aquí se crearía una notificación o solicitud
    # Por ahora solo retornamos éxito

    return JsonResponse({
        'success': True,
        'mensaje': f'Solicitud de acceso enviada para "{documento.titulo}"'
    })

@login_required
def comentarios_documento_view(request, pk):
    """Vista de comentarios del documento"""
    documento = get_object_or_404(Documento, pk=pk)

    # En una implementación completa habría un modelo ComentarioDocumento
    comentarios = []  # Placeholder

    context = {
        'title': f'Comentarios: {documento.titulo}',
        'documento': documento,
        'comentarios': comentarios,
    }
    return render(request, 'documentos/comentarios_documento.html', context)

@login_required
@require_http_methods(["POST"])
def agregar_comentario(request, pk):
    """Agregar comentario a un documento"""
    documento = get_object_or_404(Documento, pk=pk)
    form = ComentarioDocumentoForm(request.POST)

    if form.is_valid():
        # Aquí se crearía el comentario
        messages.success(request, 'Comentario agregado exitosamente.')
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'errors': form.errors}, status=400)

@login_required
def estadisticas_documentos_view(request):
    """Vista de estadísticas del sistema de documentos"""
    total_documentos = Documento.objects.count()
    total_categorias = CategoriaDocumento.objects.filter(activo=True).count()
    total_tipos = TipoDocumento.objects.filter(activo=True).count()

    # Documentos por estado
    docs_por_estado = {}
    for estado_code, estado_nombre in Documento.ESTADO_CHOICES:
        docs_por_estado[estado_nombre] = Documento.objects.filter(estado=estado_code).count()

    # Documentos por categoría (top 10)
    categorias_top = CategoriaDocumento.objects.annotate(
        num_docs=Count('documento')
    ).order_by('-num_docs')[:10]

    # Documentos más descargados
    docs_populares = Documento.objects.order_by('-total_descargas')[:10]

    # Documentos recientes
    docs_recientes = Documento.objects.order_by('-fecha_creacion')[:10]

    # Tamaño total
    total_size = Documento.objects.aggregate(
        total=Sum('tamaño_archivo')
    )['total'] or 0
    total_size_mb = round(total_size / (1024 * 1024), 2)

    context = {
        'title': 'Estadísticas de Documentos',
        'total_documentos': total_documentos,
        'total_categorias': total_categorias,
        'total_tipos': total_tipos,
        'docs_por_estado': docs_por_estado,
        'categorias_top': categorias_top,
        'docs_populares': docs_populares,
        'docs_recientes': docs_recientes,
        'total_size_mb': total_size_mb,
    }
    return render(request, 'documentos/estadisticas_documentos.html', context)

@login_required
def mis_documentos_view(request):
    """Vista de documentos del usuario actual"""
    form = FiltroMisDocumentosForm(request.GET or None)

    try:
        usuario = Usuario.objects.get(numero_documento=request.user.username)
        documentos = Documento.objects.filter(creado_por=usuario)
    except Usuario.DoesNotExist:
        documentos = Documento.objects.none()

    if form.is_valid():
        estado = form.cleaned_data.get('estado')
        categoria = form.cleaned_data.get('categoria')
        ordenar_por = form.cleaned_data.get('ordenar_por', '-fecha_modificacion')

        if estado:
            documentos = documentos.filter(estado=estado)
        if categoria:
            documentos = documentos.filter(categoria=categoria)

        documentos = documentos.order_by(ordenar_por)
    else:
        documentos = documentos.order_by('-fecha_modificacion')

    paginator = Paginator(documentos, 20)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        'title': 'Mis Documentos',
        'form': form,
        'documentos': page_obj,
        'total': documentos.count(),
    }
    return render(request, 'documentos/mis_documentos.html', context)

@login_required
def documentos_recientes_view(request):
    """Vista de documentos recientes"""
    documentos = Documento.objects.select_related(
        'tipo_documento', 'categoria', 'creado_por'
    ).order_by('-fecha_creacion')[:50]

    context = {
        'title': 'Documentos Recientes',
        'documentos': documentos,
    }
    return render(request, 'documentos/documentos_recientes.html', context)

# API Endpoints

@login_required
def buscar_documentos_api(request):
    """API para buscar documentos"""
    query = request.GET.get('q', '')

    documentos = Documento.objects.all()
    if query:
        documentos = documentos.filter(
            Q(titulo__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(contenido_texto__icontains=query)
        )

    documentos = documentos[:20]  # Limitar resultados

    results = [{
        'id': str(doc.id),
        'titulo': doc.titulo,
        'descripcion': doc.descripcion[:200],
        'categoria': doc.categoria.nombre,
        'tipo': doc.tipo_documento.nombre,
        'fecha_creacion': doc.fecha_creacion.isoformat(),
        'creado_por': doc.creado_por.nombre_completo,
    } for doc in documentos]

    return JsonResponse({
        'success': True,
        'results': results,
        'total': documentos.count(),
        'query': query
    })

@login_required
def estadisticas_documentos_api(request):
    """API de estadísticas"""
    total_documentos = Documento.objects.count()
    documentos_mes = Documento.objects.filter(
        fecha_creacion__gte=timezone.now().replace(day=1)
    ).count()
    categorias_activas = CategoriaDocumento.objects.filter(activo=True).count()

    total_size = Documento.objects.aggregate(
        total=Sum('tamaño_archivo')
    )['total'] or 0
    total_size_mb = round(total_size / (1024 * 1024), 2)

    return JsonResponse({
        'success': True,
        'estadisticas': {
            'total_documentos': total_documentos,
            'documentos_mes': documentos_mes,
            'categorias_activas': categorias_activas,
            'tamaño_total': f'{total_size_mb} MB'
        }
    })

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def subir_documento_api(request):
    """API para subir documentos"""
    try:
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            try:
                usuario = Usuario.objects.get(numero_documento=request.user.username)
                documento.creado_por = usuario
            except Usuario.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Usuario no encontrado'
                }, status=400)

            if documento.archivo:
                archivo_content = documento.archivo.read()
                documento.checksum = hashlib.sha256(archivo_content).hexdigest()
                documento.archivo.seek(0)

            documento.save()
            form.save_m2m()

            return JsonResponse({
                'success': True,
                'documento_id': str(documento.id),
                'mensaje': 'Documento subido exitosamente'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["POST"])
def validar_archivo_api(request):
    """API para validar archivos antes de subir"""
    if 'archivo' not in request.FILES:
        return JsonResponse({
            'success': False,
            'valido': False,
            'errores': ['No se proporcionó ningún archivo']
        })

    archivo = request.FILES['archivo']
    errores = []

    # Validar tamaño (100MB max)
    if archivo.size > 100 * 1024 * 1024:
        errores.append('El archivo excede el tamaño máximo de 100MB')

    # Validar extensión
    ext = archivo.name.split('.')[-1].lower()
    extensiones_permitidas = ['pdf', 'doc', 'docx', 'txt', 'xlsx', 'xls', 'ppt', 'pptx']
    if ext not in extensiones_permitidas:
        errores.append(f'Extensión .{ext} no permitida')

    return JsonResponse({
        'success': True,
        'valido': len(errores) == 0,
        'errores': errores
    })

@login_required
def importar_documentos_view(request):
    """Vista para importación masiva de documentos"""
    if request.method == 'POST':
        form = ImportarDocumentosForm(request.POST, request.FILES)
        if form.is_valid():
            # Aquí iría la lógica de importación
            messages.success(request, 'Documentos importados exitosamente.')
            return redirect('documentos:repositorio')
    else:
        form = ImportarDocumentosForm()

    context = {
        'title': 'Importar Documentos',
        'form': form,
    }
    return render(request, 'documentos/importar_documentos.html', context)

@login_required
def indexar_documentos_view(request):
    """Vista para indexar documentos"""
    context = {
        'title': 'Indexar Documentos',
        'total_documentos': Documento.objects.count(),
    }
    return render(request, 'documentos/indexar_documentos.html', context)

@login_required
def configuracion_documentos_view(request):
    """Vista de configuración del sistema de documentos"""
    if request.method == 'POST':
        form = ConfiguracionDocumentosForm(request.POST)
        if form.is_valid():
            # Guardar configuración
            messages.success(request, 'Configuración guardada exitosamente.')
            return redirect('documentos:configuracion_documentos')
    else:
        form = ConfiguracionDocumentosForm()

    context = {
        'title': 'Configuración de Documentos',
        'form': form,
    }
    return render(request, 'documentos/configuracion_documentos.html', context)
