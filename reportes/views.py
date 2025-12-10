from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Count, Q, Avg, Sum, Max, Min
from django.contrib import messages
from django.urls import reverse
from datetime import date, timedelta
import json
import uuid
from .models import Reporte, TipoReporte, MetricasRendimiento

@login_required
def dashboard_reportes_view(request):
    """Dashboard principal de reportes con estadísticas y lista completa"""
    try:
        # Filtros
        estado_filtro = request.GET.get('estado', '')
        tipo_filtro = request.GET.get('tipo', '')
        busqueda = request.GET.get('busqueda', '')

        # Estadísticas de reportes
        total_reportes = Reporte.objects.count()
        reportes_mes = Reporte.objects.filter(
            fecha_solicitud__month=timezone.now().month,
            fecha_solicitud__year=timezone.now().year
        ).count()
        tipos_disponibles = TipoReporte.objects.filter(activo=True).count()
        reportes_pendientes = Reporte.objects.filter(estado='pendiente').count()

        # Query base para lista de reportes
        reportes = Reporte.objects.select_related(
            'tipo_reporte', 'usuario_solicitante'
        ).order_by('-fecha_solicitud')

        # Aplicar filtros
        if estado_filtro:
            reportes = reportes.filter(estado=estado_filtro)

        if tipo_filtro:
            reportes = reportes.filter(tipo_reporte_id=tipo_filtro)

        if busqueda:
            reportes = reportes.filter(
                Q(titulo__icontains=busqueda) |
                Q(descripcion__icontains=busqueda) |
                Q(tipo_reporte__nombre__icontains=busqueda)
            )

        # Paginación
        paginator = Paginator(reportes, 15)  # 15 reportes por página
        page_number = request.GET.get('page')
        reportes_page = paginator.get_page(page_number)

        # Datos para filtros
        tipos_reporte = TipoReporte.objects.filter(activo=True)
        estados = Reporte.ESTADO_CHOICES

        context = {
            'title': 'Dashboard Reportes',
            'total_reportes': total_reportes,
            'reportes_mes': reportes_mes,
            'tipos_disponibles': tipos_disponibles,
            'reportes_pendientes': reportes_pendientes,
            'reportes': reportes_page,
            'tipos_reporte': tipos_reporte,
            'estados': estados,
            'estado_filtro': estado_filtro,
            'tipo_filtro': tipo_filtro,
            'busqueda': busqueda,
        }

    except Exception as e:
        messages.error(request, f'Error al cargar dashboard: {str(e)}')
        context = {'title': 'Dashboard Reportes', 'reportes': []}

    return render(request, 'reportes/dashboard_reportes.html', context)

@login_required
def visual_dashboard_view(request):
    return render(request, 'reportes/visual_dashboard.html', {'title': 'Dashboard Visual'})

@login_required
def generar_reporte_view(request):
    """Vista para mostrar formulario de generar reporte (solo GET)"""
    try:
        from maquinaria.models import CategoriaMaquina, Maquina

        # Datos para el formulario
        tipos_reporte = TipoReporte.objects.filter(activo=True)
        categorias = CategoriaMaquina.objects.filter(activa=True)
        centros_formacion = Maquina.objects.values_list('centro_formacion', flat=True).distinct().exclude(centro_formacion__isnull=True)

        context = {
            'title': 'Generar Reporte',
            'tipos_reporte': tipos_reporte,
            'categorias': categorias,
            'centros_formacion': centros_formacion,
        }

    except ImportError:
        context = {'title': 'Generar Reporte'}

    return render(request, 'reportes/generar_reporte.html', context)

@login_required
@require_http_methods(["POST"])
def crear_reporte_web(request):
    """Endpoint POST para crear reporte desde formulario web"""
    try:
        from usuarios.models import Usuario

        # Obtener datos del formulario
        tipo_reporte_id = request.POST.get('tipo_reporte')
        nombre_reporte = request.POST.get('nombre_reporte')
        descripcion = request.POST.get('descripcion', '')
        formato = request.POST.get('formato', 'pdf')

        # Validaciones básicas
        if not tipo_reporte_id:
            messages.error(request, 'El tipo de reporte es requerido')
            return redirect('reportes:generar_reporte')

        if not nombre_reporte:
            messages.error(request, 'El nombre del reporte es requerido')
            return redirect('reportes:generar_reporte')

        # Obtener filtros
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        categoria = request.POST.get('categoria')
        centro_formacion = request.POST.get('centro_formacion')
        estado_maquina = request.POST.get('estado_maquina')

        try:
            tipo_reporte = TipoReporte.objects.get(id=tipo_reporte_id)

            # Determinar usuario solicitante
            # El modelo Usuario usa numero_documento que coincide con request.user.username
            if request.user.is_authenticated:
                try:
                    usuario_solicitante = Usuario.objects.get(numero_documento=request.user.username)
                except Usuario.DoesNotExist:
                    messages.error(request, 'Tu perfil de usuario no está completo. Contacta al administrador.')
                    return redirect('reportes:generar_reporte')
            else:
                messages.error(request, 'Debes estar autenticado para crear reportes')
                return redirect('usuarios:login')

            # Crear el reporte
            reporte = Reporte.objects.create(
                tipo_reporte=tipo_reporte,
                usuario_solicitante=usuario_solicitante,
                titulo=nombre_reporte,
                descripcion=descripcion,
                formato=formato,
                fecha_inicio=fecha_inicio if fecha_inicio else None,
                fecha_fin=fecha_fin if fecha_fin else None,
                categorias_maquina=[categoria] if categoria else [],
                centros_formacion=[centro_formacion] if centro_formacion else [],
                estados_maquina=[estado_maquina] if estado_maquina else [],
                estado='pendiente'
            )

            messages.success(request, f'Reporte "{nombre_reporte}" creado exitosamente. ID: {reporte.id}')
            return redirect('reportes:detalle_reporte', pk=reporte.id)

        except TipoReporte.DoesNotExist:
            messages.error(request, 'Tipo de reporte no válido')
            return redirect('reportes:generar_reporte')

    except Exception as e:
        messages.error(request, f'Error al crear reporte: {str(e)}')
        return redirect('reportes:generar_reporte')

@csrf_exempt
@require_http_methods(["POST"])
def crear_reporte_api(request):
    """Endpoint POST API para crear un nuevo reporte"""
    try:
        from usuarios.models import Usuario

        # Verificar Content-Type
        if request.content_type == 'application/json':
            import json
            data = json.loads(request.body)
        else:
            data = request.POST

        # Obtener datos del reporte
        tipo_reporte_id = data.get('tipo_reporte')
        nombre_reporte = data.get('nombre_reporte')
        descripcion = data.get('descripcion', '')
        formato = data.get('formato', 'pdf')
        usuario_id = data.get('usuario_id')  # Para permitir especificar usuario

        # Validaciones básicas
        if not tipo_reporte_id:
            return JsonResponse({
                'success': False,
                'error': 'El tipo de reporte es requerido'
            }, status=400)

        if not nombre_reporte:
            return JsonResponse({
                'success': False,
                'error': 'El nombre del reporte es requerido'
            }, status=400)

        # Obtener filtros
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        categoria = data.get('categoria')
        centro_formacion = data.get('centro_formacion')
        estado_maquina = data.get('estado_maquina')

        try:
            tipo_reporte = TipoReporte.objects.get(id=tipo_reporte_id)

            # Determinar usuario solicitante
            if usuario_id:
                try:
                    usuario_solicitante = Usuario.objects.get(id=usuario_id)
                except Usuario.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Usuario especificado no encontrado'
                    }, status=400)
            elif request.user.is_authenticated:
                # Si el usuario está autenticado, usar su instancia de Usuario
                try:
                    usuario_solicitante = Usuario.objects.get(user=request.user)
                except Usuario.DoesNotExist:
                    # Si no existe Usuario para este User, crear uno básico o usar el primer usuario
                    usuario_solicitante = Usuario.objects.first()
                    if not usuario_solicitante:
                        return JsonResponse({
                            'success': False,
                            'error': 'No hay usuarios en el sistema'
                        }, status=400)
            else:
                # Para testing sin autenticación, usar el primer usuario disponible
                usuario_solicitante = Usuario.objects.first()
                if not usuario_solicitante:
                    return JsonResponse({
                        'success': False,
                        'error': 'No hay usuarios en el sistema para asignar el reporte'
                    }, status=400)

            # Crear el reporte
            reporte = Reporte.objects.create(
                tipo_reporte=tipo_reporte,
                usuario_solicitante=usuario_solicitante,
                titulo=nombre_reporte,
                descripcion=descripcion,
                formato=formato,
                fecha_inicio=fecha_inicio if fecha_inicio else None,
                fecha_fin=fecha_fin if fecha_fin else None,
                categorias_maquina=[categoria] if categoria else [],
                centros_formacion=[centro_formacion] if centro_formacion else [],
                estados_maquina=[estado_maquina] if estado_maquina else [],
                estado='pendiente'
            )

            # Devolver JSON (es API)
            return JsonResponse({
                'success': True,
                'message': f'Reporte "{nombre_reporte}" creado exitosamente',
                'reporte_id': str(reporte.id),
                'reporte': {
                    'id': str(reporte.id),
                    'titulo': reporte.titulo,
                    'descripcion': reporte.descripcion,
                    'estado': reporte.estado,
                    'formato': reporte.formato,
                    'fecha_solicitud': reporte.fecha_solicitud.isoformat(),
                    'tipo_reporte': reporte.tipo_reporte.nombre,
                    'usuario': reporte.usuario_solicitante.nombre_completo if hasattr(reporte.usuario_solicitante, 'nombre_completo') else str(reporte.usuario_solicitante)
                }
            }, status=201)

        except TipoReporte.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Tipo de reporte no válido'
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }, status=500)

@login_required
def lista_reportes_view(request):
    """Vista que redirige al dashboard (la lista ahora está en el dashboard)"""
    # Preservar los parámetros de búsqueda si existen
    query_string = request.GET.urlencode()
    if query_string:
        return redirect(f"{reverse('reportes:dashboard')}?{query_string}")
    return redirect('reportes:dashboard')

@login_required
def detalle_reporte_view(request, pk):
    """Vista para ver detalle de un reporte"""
    try:
        from usuarios.models import Usuario

        reporte = get_object_or_404(Reporte, id=pk)

        # Verificar que el usuario puede ver este reporte
        # Obtener el Usuario basado en el request.user.username (numero_documento)
        try:
            usuario_actual = Usuario.objects.get(numero_documento=request.user.username)
            if reporte.usuario_solicitante != usuario_actual and not request.user.is_staff:
                messages.error(request, 'No tienes permiso para ver este reporte')
                return redirect('reportes:lista_reportes')
        except Usuario.DoesNotExist:
            # Si no existe el usuario, solo permitir a staff
            if not request.user.is_staff:
                messages.error(request, 'No tienes permiso para ver este reporte')
                return redirect('reportes:lista_reportes')

        context = {
            'title': f'Reporte: {reporte.titulo}',
            'reporte': reporte,
        }

    except Exception as e:
        messages.error(request, f'Error al cargar reporte: {str(e)}')
        return redirect('reportes:lista_reportes')

    return render(request, 'reportes/detalle_reporte.html', context)

@login_required
def descargar_reporte(request, pk):
    return JsonResponse({'success': True, 'url': '/media/reportes/placeholder.pdf'})

@login_required
@require_http_methods(["POST"])
def cancelar_reporte(request, pk):
    """Vista para cancelar/eliminar un reporte"""
    try:
        from usuarios.models import Usuario

        reporte = get_object_or_404(Reporte, id=pk)

        # Verificar permisos: solo el creador o staff puede cancelar
        try:
            usuario_actual = Usuario.objects.get(numero_documento=request.user.username)
            if reporte.usuario_solicitante != usuario_actual and not request.user.is_staff:
                return JsonResponse({
                    'success': False,
                    'error': 'No tienes permiso para cancelar este reporte'
                }, status=403)
        except Usuario.DoesNotExist:
            if not request.user.is_staff:
                return JsonResponse({
                    'success': False,
                    'error': 'No tienes permiso para cancelar este reporte'
                }, status=403)

        # Guardar información antes de eliminar
        titulo_reporte = reporte.titulo

        # Eliminar el reporte
        reporte.delete()

        return JsonResponse({
            'success': True,
            'message': f'Reporte "{titulo_reporte}" eliminado correctamente'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al cancelar reporte: {str(e)}'
        }, status=500)

@login_required
def tipos_reporte_view(request):
    return render(request, 'reportes/tipos_reporte.html', {'title': 'Tipos de Reporte'})

@login_required
def crear_tipo_reporte_view(request):
    return render(request, 'reportes/crear_tipo_reporte.html', {'title': 'Crear Tipo Reporte'})

@login_required
def metricas_view(request):
    return render(request, 'reportes/metricas.html', {'title': 'Métricas'})

@login_required
def kpis_view(request):
    return render(request, 'reportes/kpis.html', {'title': 'KPIs'})

@login_required
def reporte_eficiencia_view(request):
    return render(request, 'reportes/reporte_eficiencia.html', {'title': 'Reporte Eficiencia'})

@login_required
def reporte_costos_view(request):
    return render(request, 'reportes/reporte_costos.html', {'title': 'Reporte Costos'})

@login_required
def reporte_mantenimiento_view(request):
    return render(request, 'reportes/reporte_mantenimiento.html', {'title': 'Reporte Mantenimiento'})

@login_required
def analisis_tendencias_view(request):
    return render(request, 'reportes/analisis_tendencias.html', {'title': 'Análisis Tendencias'})

@login_required
def analisis_predicciones_view(request):
    return render(request, 'reportes/analisis_predicciones.html', {'title': 'Análisis Predicciones'})

@login_required
def analisis_comparativo_view(request):
    return render(request, 'reportes/analisis_comparativo.html', {'title': 'Análisis Comparativo'})

@login_required
def exportar_excel_view(request):
    return HttpResponse('Excel export placeholder', content_type='application/vnd.ms-excel')

@login_required
def exportar_pdf_view(request):
    return HttpResponse('PDF export placeholder', content_type='application/pdf')

@login_required
def exportar_csv_view(request):
    return HttpResponse('CSV export placeholder', content_type='text/csv')

@login_required
def datos_widget_api(request, widget_id):
    return JsonResponse({'data': [], 'widget_id': widget_id})

@login_required
def grafico_eficiencia_api(request):
    """API para gráfico de eficiencia de máquinas"""
    try:
        from maquinaria.models import Maquina, CategoriaMaquina

        # Eficiencia por categoría
        categorias_eficiencia = CategoriaMaquina.objects.annotate(
            avg_eficiencia=Avg('maquina__eficiencia')
        ).filter(avg_eficiencia__isnull=False)

        labels = []
        data = []
        colors = []

        for categoria in categorias_eficiencia:
            labels.append(categoria.nombre)
            data.append(round(categoria.avg_eficiencia, 1))
            colors.append(categoria.color)

        return JsonResponse({
            'labels': labels,
            'data': data,
            'colors': colors
        })

    except ImportError:
        return JsonResponse({'labels': [], 'data': [], 'colors': []})

@login_required
def grafico_costos_api(request):
    """API para gráfico de costos de mantenimiento"""
    try:
        from maquinaria.models import HistorialMaquina
        from django.db.models import Sum

        # Costos por mes (últimos 6 meses)
        hoy = date.today()
        labels = []
        data = []

        for i in range(6):
            mes_fecha = hoy - timedelta(days=30*i)
            mes_nombre = mes_fecha.strftime('%B')

            # Calcular costos del mes
            costos_mes = HistorialMaquina.objects.filter(
                fecha_evento__year=mes_fecha.year,
                fecha_evento__month=mes_fecha.month,
                costo_asociado__isnull=False
            ).aggregate(total=Sum('costo_asociado'))['total'] or 0

            labels.insert(0, mes_nombre)
            data.insert(0, float(costos_mes))

        return JsonResponse({
            'labels': labels,
            'data': data
        })

    except ImportError:
        return JsonResponse({'labels': [], 'data': []})

@login_required
def grafico_estados_api(request):
    """API para gráfico de estados de máquinas"""
    try:
        from maquinaria.models import Maquina

        estados_data = Maquina.objects.values('estado').annotate(
            count=Count('id')
        ).order_by('-count')

        labels = []
        data = []
        colors = ['#28a745', '#ffc107', '#dc3545', '#17a2b8', '#6c757d']

        for i, estado in enumerate(estados_data):
            labels.append(estado['estado'].replace('_', ' ').title())
            data.append(estado['count'])

        return JsonResponse({
            'labels': labels,
            'data': data,
            'colors': colors[:len(labels)]
        })

    except ImportError:
        return JsonResponse({'labels': [], 'data': [], 'colors': []})

@login_required
def tabla_maquinas_api(request):
    """API para tabla de máquinas con datos reales"""
    try:
        from maquinaria.models import Maquina

        maquinas = Maquina.objects.select_related('categoria', 'proveedor').all()[:20]

        data = []
        for maquina in maquinas:
            data.append({
                'codigo': maquina.codigo_inventario,
                'nombre': maquina.nombre,
                'categoria': maquina.categoria.nombre if maquina.categoria else '-',
                'estado': maquina.get_estado_display(),
                'condicion': maquina.get_condicion_display(),
                'eficiencia': f"{maquina.eficiencia}%",
                'horas_uso': maquina.horas_uso_total,
                'ultimo_mantenimiento': maquina.fecha_ultimo_mantenimiento.strftime('%Y-%m-%d') if maquina.fecha_ultimo_mantenimiento else '-',
            })

        return JsonResponse({'data': data})

    except ImportError:
        return JsonResponse({'data': []})

@login_required
def personalizar_dashboard_view(request):
    return render(request, 'reportes/personalizar_dashboard.html', {'title': 'Personalizar Dashboard'})

@login_required
@require_http_methods(["POST"])
def agregar_widget_dashboard(request):
    return JsonResponse({'success': True})

@login_required
@require_http_methods(["POST"])
def eliminar_widget_dashboard(request, pk):
    return JsonResponse({'success': True})

@login_required
def filtros_centros_api(request):
    return JsonResponse({'centros': []})

@login_required
def filtros_categorias_api(request):
    return JsonResponse({'categorias': []})

@login_required
def aplicar_filtros_api(request):
    return JsonResponse({'success': True, 'data': []})

@login_required
def reportes_programados_view(request):
    return render(request, 'reportes/reportes_programados.html', {'title': 'Reportes Programados'})

@login_required
def crear_reporte_programado_view(request):
    return render(request, 'reportes/crear_reporte_programado.html', {'title': 'Crear Reporte Programado'})
