from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.urls import reverse
from .models import Maquina, CategoriaMaquina, Proveedor, AlertaMaquina, HistorialMaquina, MantenimientoProgramado, UsoMaquinaria
from .forms import UsoMaquinariaForm
from usuarios.models import Usuario

# Dashboard
@login_required
def dashboard_view(request):
    """Dashboard principal de maquinaria con estadísticas reales y lista de máquinas"""
    # Estadísticas básicas
    total_maquinas = Maquina.objects.count()
    maquinas_operativas = Maquina.objects.filter(estado='operativa').count()
    maquinas_mantenimiento = Maquina.objects.filter(estado='mantenimiento').count()
    alertas_activas = AlertaMaquina.objects.filter(estado='activa').count()

    # Alertas recientes
    alertas_recientes = AlertaMaquina.objects.select_related(
        'maquina'
    ).filter(estado='activa').order_by('-fecha_creacion')[:5]

    # Lista de máquinas con filtros (igual que lista_maquinas_view)
    maquinas_list = Maquina.objects.select_related('categoria', 'proveedor', 'responsable').all()

    estado_filtro = request.GET.get('estado')
    categoria_filtro = request.GET.get('categoria')
    busqueda = request.GET.get('busqueda')

    if estado_filtro:
        maquinas_list = maquinas_list.filter(estado=estado_filtro)
    if categoria_filtro:
        maquinas_list = maquinas_list.filter(categoria_id=categoria_filtro)
    if busqueda:
        maquinas_list = maquinas_list.filter(
            Q(codigo_inventario__icontains=busqueda) |
            Q(nombre__icontains=busqueda) |
            Q(marca__icontains=busqueda) |
            Q(modelo__icontains=busqueda)
        )

    paginator = Paginator(maquinas_list, 20)
    page = request.GET.get('page')
    maquinas = paginator.get_page(page)

    categorias = CategoriaMaquina.objects.filter(activa=True)

    context = {
        'title': 'Dashboard Maquinaria',
        'total_maquinas': total_maquinas,
        'maquinas_operativas': maquinas_operativas,
        'maquinas_mantenimiento': maquinas_mantenimiento,
        'alertas_activas': alertas_activas,
        'alertas_recientes': alertas_recientes,
        'maquinas': maquinas,
        'categorias': categorias,
        'estado_filtro': estado_filtro,
        'categoria_filtro': categoria_filtro,
        'busqueda': busqueda,
    }

    return render(request, 'maquinaria/dashboard.html', context)

# CRUD de máquinas
@login_required
def lista_maquinas_view(request):
    """Lista todas las máquinas con filtros y paginación"""
    maquinas_list = Maquina.objects.select_related('categoria', 'proveedor', 'responsable').all()

    # Filtros
    estado_filtro = request.GET.get('estado')
    categoria_filtro = request.GET.get('categoria')
    busqueda = request.GET.get('busqueda')

    if estado_filtro:
        maquinas_list = maquinas_list.filter(estado=estado_filtro)

    if categoria_filtro:
        maquinas_list = maquinas_list.filter(categoria_id=categoria_filtro)

    if busqueda:
        maquinas_list = maquinas_list.filter(
            Q(codigo_inventario__icontains=busqueda) |
            Q(nombre__icontains=busqueda) |
            Q(marca__icontains=busqueda) |
            Q(modelo__icontains=busqueda)
        )

    # Paginación
    paginator = Paginator(maquinas_list, 20)
    page = request.GET.get('page')
    maquinas = paginator.get_page(page)

    # Para los filtros en template
    categorias = CategoriaMaquina.objects.filter(activa=True)

    context = {
        'title': 'Lista de Máquinas',
        'maquinas': maquinas,
        'categorias': categorias,
        'estado_filtro': estado_filtro,
        'categoria_filtro': categoria_filtro,
        'busqueda': busqueda,
    }

    return render(request, 'maquinaria/lista_maquinas.html', context)

@login_required
def crear_maquina_view(request):
    """Crear nueva máquina"""
    from .forms import MaquinaForm

    if request.method == 'POST':
        form = MaquinaForm(request.POST, request.FILES)
        if form.is_valid():
            maquina = form.save(commit=False)

            # Asignar usuario creador
            try:
                usuario = Usuario.objects.get(numero_documento=request.user.username)
                maquina.created_by = usuario
            except Usuario.DoesNotExist:
                pass

            maquina.save()

            # Crear entrada en el historial
            HistorialMaquina.objects.create(
                maquina=maquina,
                tipo_evento='creacion',
                descripcion=f'Máquina {maquina.codigo_inventario} creada en el sistema',
                usuario=maquina.created_by
            )

            messages.success(request, f'Máquina {maquina.codigo_inventario} creada exitosamente')
            return redirect('maquinaria:detalle_maquina', pk=maquina.pk)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = MaquinaForm()

    context = {
        'title': 'Crear Máquina',
        'form': form,
    }

    return render(request, 'maquinaria/crear_maquina.html', context)

@login_required
def detalle_maquina_view(request, pk):
    """Detalle de una máquina específica"""
    maquina = get_object_or_404(Maquina, pk=pk)
    historial = HistorialMaquina.objects.filter(maquina=maquina).order_by('-fecha_evento')[:10]
    alertas = AlertaMaquina.objects.filter(maquina=maquina).order_by('-fecha_creacion')[:5]

    context = {
        'title': f'Detalle - {maquina.codigo_inventario}',
        'maquina': maquina,
        'historial': historial,
        'alertas': alertas,
    }

    return render(request, 'maquinaria/detalle_maquina.html', context)

@login_required
def editar_maquina_view(request, pk):
    """Editar máquina existente"""
    from .forms import MaquinaForm

    maquina = get_object_or_404(Maquina, pk=pk)

    if request.method == 'POST':
        form = MaquinaForm(request.POST, request.FILES, instance=maquina)
        if form.is_valid():
            # Verificar qué campos cambiaron
            campos_cambiados = []
            for field_name, field in form.fields.items():
                old_value = getattr(maquina, field_name, None)
                new_value = form.cleaned_data.get(field_name)
                if old_value != new_value:
                    campos_cambiados.append(field_name)

            maquina_actualizada = form.save()

            # Crear entrada en el historial si hubo cambios
            if campos_cambiados:
                try:
                    usuario = Usuario.objects.get(numero_documento=request.user.username)
                except Usuario.DoesNotExist:
                    usuario = None

                HistorialMaquina.objects.create(
                    maquina=maquina_actualizada,
                    tipo_evento='actualizacion',
                    descripcion=f'Máquina actualizada. Campos modificados: {", ".join(campos_cambiados)}',
                    usuario=usuario
                )

            messages.success(request, f'Máquina {maquina.codigo_inventario} actualizada exitosamente')
            return redirect('maquinaria:detalle_maquina', pk=pk)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = MaquinaForm(instance=maquina)

    context = {
        'title': f'Editar - {maquina.codigo_inventario}',
        'maquina': maquina,
        'form': form,
    }

    return render(request, 'maquinaria/editar_maquina.html', context)

@login_required
def eliminar_maquina_view(request, pk):
    """Eliminar máquina guardando todo su historial"""
    from .models import MaquinaEliminada
    from django.core.serializers import serialize
    from decimal import Decimal
    import json

    maquina = get_object_or_404(Maquina, pk=pk)

    if request.method == 'POST':
        codigo = maquina.codigo_inventario
        nombre = maquina.nombre
        motivo = request.POST.get('motivo_eliminacion', '')

        # Obtener usuario
        try:
            usuario = Usuario.objects.get(numero_documento=request.user.username)
        except Usuario.DoesNotExist:
            usuario = None

        # ===== GUARDAR TODA LA INFORMACIÓN ANTES DE ELIMINAR =====

        # 1. Recopilar datos completos de la máquina
        datos_maquina = {
            'codigo_inventario': maquina.codigo_inventario,
            'nombre': maquina.nombre,
            'categoria': maquina.categoria.nombre if maquina.categoria else None,
            'marca': maquina.marca,
            'modelo': maquina.modelo,
            'numero_serie': maquina.numero_serie,
            'estado': maquina.estado,
            'condicion': maquina.condicion,
            'especificaciones_tecnicas': maquina.especificaciones_tecnicas,
            'capacidad': maquina.capacidad,
            'potencia': maquina.potencia,
            'voltaje': maquina.voltaje,
            'dimensiones': maquina.dimensiones,
            'peso': maquina.peso,
            'ubicacion': maquina.ubicacion,
            'centro_formacion': maquina.centro_formacion,
            'ambiente_formacion': maquina.ambiente_formacion,
            'responsable': maquina.responsable.nombre_completo if maquina.responsable else None,
            'proveedor': maquina.proveedor.nombre if maquina.proveedor else None,
            'fecha_adquisicion': str(maquina.fecha_adquisicion),
            'valor_adquisicion': float(maquina.valor_adquisicion),
            'numero_factura': maquina.numero_factura,
            'garantia_meses': maquina.garantia_meses,
            'horas_uso_total': float(maquina.horas_uso_total),
            'horas_uso_mes': float(maquina.horas_uso_mes),
            'eficiencia': float(maquina.eficiencia),
            'fecha_ultimo_mantenimiento': str(maquina.fecha_ultimo_mantenimiento) if maquina.fecha_ultimo_mantenimiento else None,
            'proximo_mantenimiento': str(maquina.proximo_mantenimiento) if maquina.proximo_mantenimiento else None,
            'frecuencia_mantenimiento_dias': maquina.frecuencia_mantenimiento_dias,
            'observaciones': maquina.observaciones,
            'created_at': str(maquina.created_at),
            'updated_at': str(maquina.updated_at),
            'created_by': maquina.created_by.nombre_completo if maquina.created_by else None,
        }

        # 2. Recopilar TODO el historial
        historial = []
        for evento in HistorialMaquina.objects.filter(maquina=maquina).order_by('fecha_evento'):
            historial.append({
                'tipo_evento': evento.tipo_evento,
                'descripcion': evento.descripcion,
                'valor_anterior': evento.valor_anterior,
                'valor_nuevo': evento.valor_nuevo,
                'costo_asociado': float(evento.costo_asociado) if evento.costo_asociado else 0,
                'fecha_evento': str(evento.fecha_evento),
                'usuario': evento.usuario.nombre_completo if evento.usuario else 'Sistema',
            })

        # 3. Recopilar TODAS las alertas
        alertas = []
        for alerta in AlertaMaquina.objects.filter(maquina=maquina).order_by('fecha_creacion'):
            alertas.append({
                'tipo': alerta.tipo,
                'prioridad': alerta.prioridad,
                'titulo': alerta.titulo,
                'descripcion': alerta.descripcion,
                'estado': alerta.estado,
                'fecha_creacion': str(alerta.fecha_creacion),
                'fecha_resolucion': str(alerta.fecha_resolucion) if alerta.fecha_resolucion else None,
                'resuelto_por': alerta.resuelto_por.nombre_completo if alerta.resuelto_por else None,
                'notas_resolucion': alerta.notas_resolucion,
                'created_by': alerta.created_by.nombre_completo if alerta.created_by else None,
            })

        # 4. Recopilar TODOS los mantenimientos
        mantenimientos = []
        total_costo_mantenimiento = Decimal('0.00')
        for mant in MantenimientoProgramado.objects.filter(maquina=maquina).order_by('fecha_programada'):
            costo = mant.costo_real if mant.costo_real else mant.costo_estimado
            if costo:
                total_costo_mantenimiento += costo

            mantenimientos.append({
                'tipo': mant.tipo,
                'titulo': mant.titulo,
                'descripcion': mant.descripcion,
                'prioridad': mant.prioridad,
                'estado': mant.estado,
                'fecha_programada': str(mant.fecha_programada),
                'fecha_inicio_real': str(mant.fecha_inicio_real) if mant.fecha_inicio_real else None,
                'fecha_fin_real': str(mant.fecha_fin_real) if mant.fecha_fin_real else None,
                'tecnico_asignado': mant.tecnico_asignado.nombre_completo if mant.tecnico_asignado else None,
                'tecnico_realizado': mant.tecnico_realizado.nombre_completo if mant.tecnico_realizado else None,
                'trabajo_realizado': mant.trabajo_realizado,
                'observaciones': mant.observaciones,
                'problemas_encontrados': mant.problemas_encontrados,
                'costo_estimado': float(mant.costo_estimado) if mant.costo_estimado else 0,
                'costo_real': float(mant.costo_real) if mant.costo_real else 0,
                'costo_repuestos': float(mant.costo_repuestos) if mant.costo_repuestos else 0,
                'costo_mano_obra': float(mant.costo_mano_obra) if mant.costo_mano_obra else 0,
                'componentes_revisar': mant.componentes_revisar,
                'herramientas_necesarias': mant.herramientas_necesarias,
                'repuestos_utilizados': mant.repuestos_utilizados,
            })

        # 5. Calcular estadísticas
        total_mantenimientos = mantenimientos_count = HistorialMaquina.objects.filter(
            maquina=maquina, tipo_evento='mantenimiento'
        ).count()

        total_reparaciones = HistorialMaquina.objects.filter(
            maquina=maquina, tipo_evento='reparacion'
        ).count()

        dias_operacion = 0
        if maquina.fecha_adquisicion:
            from django.utils import timezone
            dias_operacion = (timezone.now().date() - maquina.fecha_adquisicion).days

        # 6. Crear registro de máquina eliminada
        maquina_eliminada = MaquinaEliminada.objects.create(
            codigo_inventario=codigo,
            nombre=nombre,
            marca=maquina.marca,
            modelo=maquina.modelo,
            numero_serie=maquina.numero_serie,
            categoria_nombre=maquina.categoria.nombre if maquina.categoria else 'Sin categoría',
            estado_final=maquina.estado,
            condicion_final=maquina.condicion,
            ubicacion=maquina.ubicacion,
            centro_formacion=maquina.centro_formacion,
            horas_uso_total=maquina.horas_uso_total,
            eficiencia_final=maquina.eficiencia,
            datos_completos_maquina=datos_maquina,
            historial_completo=historial,
            alertas_asociadas=alertas,
            mantenimientos_realizados=mantenimientos,
            eliminado_por=usuario,
            motivo_eliminacion=motivo,
            total_mantenimientos=total_mantenimientos,
            total_reparaciones=total_reparaciones,
            total_alertas=len(alertas),
            costo_total_mantenimiento=total_costo_mantenimiento,
            dias_operacion=dias_operacion,
        )

        # 7. Eliminar la máquina (esto eliminará historial, alertas, etc. por CASCADE)
        maquina.delete()

        messages.success(
            request,
            f'Máquina {codigo} eliminada exitosamente. '
            f'Se guardó un registro completo con {len(historial)} eventos, '
            f'{len(alertas)} alertas y {len(mantenimientos)} mantenimientos.'
        )
        return redirect('maquinaria:dashboard')

    # GET request - mostrar confirmación
    total_alertas = AlertaMaquina.objects.filter(maquina=maquina).count()
    total_historial = HistorialMaquina.objects.filter(maquina=maquina).count()
    total_mantenimientos = MantenimientoProgramado.objects.filter(maquina=maquina).count()

    context = {
        'title': f'Eliminar - {maquina.codigo_inventario}',
        'maquina': maquina,
        'total_alertas': total_alertas,
        'total_historial': total_historial,
        'total_mantenimientos': total_mantenimientos,
    }

    return render(request, 'maquinaria/eliminar_maquina.html', context)

# Estado de máquinas
@login_required
def cambiar_estado_maquina(request, pk):
    """Cambiar el estado de una máquina vía AJAX"""
    if request.method == 'POST':
        maquina = get_object_or_404(Maquina, pk=pk)
        nuevo_estado = request.POST.get('estado')
        observaciones = request.POST.get('observaciones', '')

        if nuevo_estado in dict(Maquina.ESTADO_CHOICES):
            estado_anterior = maquina.estado
            maquina.estado = nuevo_estado
            maquina.save()

            # Crear entrada en el historial
            try:
                usuario = Usuario.objects.get(numero_documento=request.user.username)
            except Usuario.DoesNotExist:
                usuario = None

            HistorialMaquina.objects.create(
                maquina=maquina,
                tipo_evento='cambio_estado',
                descripcion=f'Estado cambiado de "{estado_anterior}" a "{nuevo_estado}". {observaciones}',
                valor_anterior=estado_anterior,
                valor_nuevo=nuevo_estado,
                usuario=usuario
            )

            return JsonResponse({
                'success': True,
                'message': f'Estado cambiado exitosamente a {maquina.get_estado_display()}'
            })

        return JsonResponse({
            'success': False,
            'message': 'Estado inválido'
        })

    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@login_required
def historial_maquina_view(request, pk):
    return render(request, 'maquinaria/historial_maquina.html', {'title': 'Historial Máquina'})

# Categorías y proveedores
@login_required
def categorias_view(request):
    return render(request, 'maquinaria/categorias.html', {'title': 'Categorías'})

@login_required
def crear_categoria_view(request):
    return render(request, 'maquinaria/crear_categoria.html', {'title': 'Crear Categoría'})

@login_required
def proveedores_view(request):
    return render(request, 'maquinaria/proveedores.html', {'title': 'Proveedores'})

@login_required
def crear_proveedor_view(request):
    return render(request, 'maquinaria/crear_proveedor.html', {'title': 'Crear Proveedor'})

# Alertas
@login_required
def alertas_view(request):
    """Lista de alertas con filtros y estadísticas reales"""
    alertas_list = AlertaMaquina.objects.select_related('maquina').all()

    # Filtros
    estado_filtro = request.GET.get('estado')
    prioridad_filtro = request.GET.get('prioridad')
    tipo_filtro = request.GET.get('tipo')

    if estado_filtro:
        alertas_list = alertas_list.filter(estado=estado_filtro)

    if prioridad_filtro:
        alertas_list = alertas_list.filter(prioridad=prioridad_filtro)

    if tipo_filtro:
        alertas_list = alertas_list.filter(tipo=tipo_filtro)

    # Estadísticas reales de alertas
    from django.utils import timezone
    from datetime import date

    alertas_criticas = AlertaMaquina.objects.filter(
        estado='activa', prioridad='critica'
    ).count()

    alertas_altas = AlertaMaquina.objects.filter(
        estado='activa', prioridad='alta'
    ).count()

    alertas_medias = AlertaMaquina.objects.filter(
        estado='activa', prioridad='media'
    ).count()

    alertas_resueltas_hoy = AlertaMaquina.objects.filter(
        estado='resuelta',
        fecha_resolucion__date=date.today()
    ).count()

    # Estadísticas por tipo
    from django.db.models import Count
    tipos_alertas = AlertaMaquina.objects.filter(
        estado='activa'
    ).values('tipo').annotate(
        count=Count('id')
    ).order_by('-count')

    # Paginación
    paginator = Paginator(alertas_list.order_by('-fecha_creacion'), 15)
    page = request.GET.get('page')
    alertas = paginator.get_page(page)

    context = {
        'title': 'Alertas de Maquinaria',
        'alertas': alertas,
        'estado_filtro': estado_filtro,
        'prioridad_filtro': prioridad_filtro,
        'tipo_filtro': tipo_filtro,
        'alertas_criticas': alertas_criticas,
        'alertas_altas': alertas_altas,
        'alertas_medias': alertas_medias,
        'alertas_resueltas_hoy': alertas_resueltas_hoy,
        'tipos_alertas': tipos_alertas,
    }

    return render(request, 'maquinaria/alertas.html', context)

@login_required
def crear_alerta_view(request):
    """Crear nueva alerta con datos reales"""
    from .forms import AlertaMaquinaForm
    import json

    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            maquina_id = request.POST.get('maquina')
            tipo_alerta = request.POST.get('tipo_alerta', 'mantenimiento')
            titulo = request.POST.get('titulo')
            prioridad = request.POST.get('prioridad', 'media')
            descripcion = request.POST.get('descripcion')
            categoria = request.POST.get('categoria')
            fecha_deteccion = request.POST.get('fecha_deteccion')
            detectado_por = request.POST.get('detectado_por', 'sistema')
            ubicacion_falla = request.POST.get('ubicacion_falla', '')
            impacto_operacional = request.POST.get('impacto_operacional', 'minimo')
            riesgo_seguridad = request.POST.get('riesgo_seguridad', 'nulo')
            tecnico_asignado = request.POST.get('tecnico_asignado')
            fecha_estimada = request.POST.get('fecha_estimada')

            # Obtener síntomas y acciones inmediatas
            sintomas = request.POST.getlist('sintomas')
            acciones_inmediatas = request.POST.getlist('acciones_inmediatas')

            # Validar datos requeridos
            if not all([maquina_id, titulo, descripcion]):
                messages.error(request, 'Por favor complete todos los campos requeridos.')
                return redirect('maquinaria:crear_alerta')

            # Obtener la máquina
            try:
                maquina = Maquina.objects.get(pk=maquina_id)
            except Maquina.DoesNotExist:
                messages.error(request, 'La máquina seleccionada no existe.')
                return redirect('maquinaria:crear_alerta')

            # Mapear tipo de alerta al modelo
            tipo_mapping = {
                'falla': 'reparacion',
                'mantenimiento': 'mantenimiento',
                'operacional': 'eficiencia'
            }
            tipo_modelo = tipo_mapping.get(tipo_alerta, 'mantenimiento')

            # Crear la alerta
            alerta = AlertaMaquina.objects.create(
                maquina=maquina,
                tipo=tipo_modelo,
                prioridad=prioridad,
                titulo=titulo,
                descripcion=descripcion,
                estado='activa'
            )

            # Obtener usuario creador
            try:
                usuario = Usuario.objects.get(numero_documento=request.user.username)
                alerta.created_by = usuario
                alerta.save()
            except Usuario.DoesNotExist:
                pass

            # Crear entrada en el historial
            datos_adicionales = {
                'categoria': categoria,
                'detectado_por': detectado_por,
                'ubicacion_falla': ubicacion_falla,
                'sintomas': sintomas,
                'impacto_operacional': impacto_operacional,
                'riesgo_seguridad': riesgo_seguridad,
                'acciones_inmediatas': acciones_inmediatas,
                'tecnico_asignado': tecnico_asignado,
                'fecha_estimada': fecha_estimada
            }

            HistorialMaquina.objects.create(
                maquina=maquina,
                tipo_evento='alerta_creada',
                descripcion=f'Alerta creada: {titulo} (Prioridad: {prioridad})',
                valor_nuevo=json.dumps(datos_adicionales, ensure_ascii=False),
                usuario=alerta.created_by
            )

            # Actualizar estado de máquina si es crítica
            if prioridad in ['critica', 'emergencia']:
                estado_anterior = maquina.estado
                if 'suspender_operacion' in acciones_inmediatas:
                    maquina.estado = 'fuera_servicio'
                    maquina.save()

                    # Crear entrada adicional en historial para cambio de estado
                    HistorialMaquina.objects.create(
                        maquina=maquina,
                        tipo_evento='cambio_estado',
                        descripcion=f'Estado cambiado automáticamente por alerta crítica: {titulo}',
                        valor_anterior=estado_anterior,
                        valor_nuevo=maquina.estado,
                        usuario=alerta.created_by
                    )

            messages.success(request, f'Alerta "{titulo}" creada exitosamente para {maquina.codigo_inventario}')
            return redirect('maquinaria:detalle_alerta', pk=alerta.pk)

        except Exception as e:
            messages.error(request, f'Error al crear la alerta: {str(e)}')
            return redirect('maquinaria:crear_alerta')

    # GET request - mostrar formulario
    try:
        # Intentar obtener usuarios con filtro, si falla usar todos los usuarios
        usuarios_tecnicos = Usuario.objects.all().order_by('first_name', 'last_name')[:20]  # Limitar a 20 para performance
    except Exception:
        usuarios_tecnicos = []

    context = {
        'title': 'Crear Alerta',
        'maquinas': Maquina.objects.select_related('categoria').all().order_by('codigo_inventario'),
        'usuarios_tecnicos': usuarios_tecnicos,
    }

    return render(request, 'maquinaria/crear_alerta.html', context)

@login_required
def resolver_alerta(request, pk):
    """Resolver alerta via AJAX"""
    alerta = get_object_or_404(AlertaMaquina, pk=pk)

    if request.method == 'POST':
        alerta.estado = 'resuelta'
        alerta.fecha_resolucion = timezone.now()

        try:
            usuario = Usuario.objects.get(numero_documento=request.user.username)
            alerta.resuelto_por = usuario
        except Usuario.DoesNotExist:
            pass

        alerta.save()

        # Crear entrada en el historial
        HistorialMaquina.objects.create(
            maquina=alerta.maquina,
            tipo_evento='alerta_resuelta',
            descripcion=f'Alerta resuelta: {alerta.titulo}',
            usuario=alerta.resuelto_por
        )

        return JsonResponse({'success': True, 'message': 'Alerta resuelta exitosamente'})

    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@login_required
@login_required
def reporte_pdf_alerta(request, pk):
    """Genera un PDF con el detalle completo de una alerta."""
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    import io

    alerta = get_object_or_404(AlertaMaquina, pk=pk)

    VERDE  = colors.HexColor('#39a900')
    MARINO = colors.HexColor('#00324d')
    NARANJA = colors.HexColor('#ff6b35')
    ROJO   = colors.HexColor('#cc4400')
    GRIS   = colors.HexColor('#f8f9fa')
    GRIS_B = colors.HexColor('#dee2e6')

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    estilo_titulo    = ParagraphStyle('t', fontSize=18, fontName='Helvetica-Bold', textColor=MARINO, spaceAfter=4)
    estilo_subtitulo = ParagraphStyle('s', fontSize=11, fontName='Helvetica', textColor=colors.HexColor('#6c757d'), spaceAfter=12)
    estilo_seccion   = ParagraphStyle('sec', fontSize=12, fontName='Helvetica-Bold', textColor=colors.white, spaceAfter=6)
    estilo_normal    = ParagraphStyle('n', fontSize=10, fontName='Helvetica', spaceAfter=4, leading=14)
    estilo_label     = ParagraphStyle('l', fontSize=9,  fontName='Helvetica-Bold', textColor=colors.HexColor('#6c757d'), spaceAfter=2)
    estilo_valor     = ParagraphStyle('v', fontSize=10, fontName='Helvetica', spaceAfter=8, leading=13)

    COLOR_PRIORIDAD = {'critica': ROJO, 'alta': ROJO, 'media': NARANJA, 'baja': VERDE}
    color_prio = COLOR_PRIORIDAD.get(alerta.prioridad, MARINO)

    COLOR_ESTADO = {'activa': NARANJA, 'en_proceso': MARINO, 'resuelta': VERDE, 'ignorada': colors.grey}
    color_estado = COLOR_ESTADO.get(alerta.estado, MARINO)

    def cabecera_seccion(texto, color=MARINO):
        data = [[Paragraph(f'<font color="white"><b>{texto}</b></font>', estilo_seccion)]]
        t = Table(data, colWidths=[17*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), color),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [color]),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
        ]))
        return t

    def fila_dato(label, valor):
        return [Paragraph(label, estilo_label), Paragraph(str(valor) if valor else '—', estilo_valor)]

    story = []

    # ── Encabezado ──────────────────────────────────────────────────────────
    header_data = [[
        Paragraph('SENA Maquinaria', ParagraphStyle('hb', fontSize=14, fontName='Helvetica-Bold', textColor=colors.white)),
        Paragraph('REPORTE DE ALERTA', ParagraphStyle('hr', fontSize=14, fontName='Helvetica-Bold', textColor=colors.white, alignment=2)),
    ]]
    header_t = Table(header_data, colWidths=[8.5*cm, 8.5*cm])
    header_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), MARINO),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
    ]))
    story.append(header_t)
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph(alerta.titulo, estilo_titulo))
    story.append(Paragraph(
        f'Alerta #{alerta.pk}  •  Máquina: {alerta.maquina.codigo_inventario}  •  '
        f'Generada: {alerta.fecha_creacion.strftime("%d/%m/%Y %H:%M")}',
        estilo_subtitulo))

    # Badges prioridad / estado
    badges_data = [[
        Paragraph(f'<font color="white"><b> {alerta.get_prioridad_display().upper()} </b></font>',
                  ParagraphStyle('b1', fontSize=10, fontName='Helvetica-Bold')),
        Paragraph(f'<font color="white"><b> {alerta.get_estado_display().upper()} </b></font>',
                  ParagraphStyle('b2', fontSize=10, fontName='Helvetica-Bold')),
        Paragraph('', styles['Normal']),
    ]]
    bt = Table(badges_data, colWidths=[3.5*cm, 3.5*cm, 10*cm])
    bt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), color_prio),
        ('BACKGROUND', (1,0), (1,0), color_estado),
        ('BACKGROUND', (2,0), (2,0), colors.white),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
    ]))
    story.append(bt)
    story.append(Spacer(1, 0.5*cm))

    # ── Información de la Alerta ─────────────────────────────────────────────
    story.append(cabecera_seccion('  Información de la Alerta'))
    story.append(Spacer(1, 0.2*cm))

    info_data = [
        fila_dato('Máquina afectada', f'{alerta.maquina.nombre} ({alerta.maquina.codigo_inventario})'),
        fila_dato('Tipo de alerta',   alerta.get_tipo_display()),
        fila_dato('Prioridad',        alerta.get_prioridad_display()),
        fila_dato('Estado',           alerta.get_estado_display()),
        fila_dato('Fecha detección',  alerta.fecha_creacion.strftime('%d/%m/%Y %H:%M:%S')),
        fila_dato('Registrada por',   f'{alerta.created_by.nombres} {alerta.created_by.apellidos}' if alerta.created_by else 'Sistema Automático'),
    ]
    info_t = Table(info_data, colWidths=[5*cm, 12*cm])
    info_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), GRIS),
        ('GRID', (0,0), (-1,-1), 0.5, GRIS_B),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(info_t)
    story.append(Spacer(1, 0.4*cm))

    # ── Técnico Asignado ─────────────────────────────────────────────────────
    story.append(cabecera_seccion('  Técnico Asignado', VERDE))
    story.append(Spacer(1, 0.2*cm))
    if alerta.tecnico_asignado:
        tec = alerta.tecnico_asignado
        tec_data = [
            fila_dato('Nombre completo', f'{tec.nombres} {tec.apellidos}'),
            fila_dato('Cargo',           tec.cargo),
            fila_dato('Correo',          tec.email),
            fila_dato('Teléfono',        tec.telefono if hasattr(tec, 'telefono') and tec.telefono else '—'),
            fila_dato('Documento',       f'{tec.tipo_documento} {tec.numero_documento}'),
        ]
        tec_t = Table(tec_data, colWidths=[5*cm, 12*cm])
        tec_t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), GRIS),
            ('GRID', (0,0), (-1,-1), 0.5, GRIS_B),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(tec_t)
    else:
        story.append(Paragraph('<i>Sin técnico asignado al momento de generar el reporte.</i>', estilo_normal))
    story.append(Spacer(1, 0.4*cm))

    # ── Descripción ──────────────────────────────────────────────────────────
    story.append(cabecera_seccion('  Descripción de la Alerta'))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(alerta.descripcion.replace('\n', '<br/>'), estilo_normal))
    story.append(Spacer(1, 0.4*cm))

    # ── Resolución (si aplica) ───────────────────────────────────────────────
    if alerta.estado == 'resuelta':
        story.append(cabecera_seccion('  Resolución', VERDE))
        story.append(Spacer(1, 0.2*cm))
        res_data = [
            fila_dato('Fecha resolución', alerta.fecha_resolucion.strftime('%d/%m/%Y %H:%M:%S') if alerta.fecha_resolucion else '—'),
            fila_dato('Resuelto por', f'{alerta.resuelto_por.nombres} {alerta.resuelto_por.apellidos}' if alerta.resuelto_por else '—'),
            fila_dato('Notas', alerta.notas_resolucion or '—'),
        ]
        res_t = Table(res_data, colWidths=[5*cm, 12*cm])
        res_t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), GRIS),
            ('GRID', (0,0), (-1,-1), 0.5, GRIS_B),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(res_t)
        story.append(Spacer(1, 0.4*cm))

    # ── Pie de página ────────────────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=1, color=GRIS_B))
    story.append(Spacer(1, 0.2*cm))
    from django.utils import timezone
    story.append(Paragraph(
        f'<font color="#6c757d" size="8">Reporte generado el {timezone.localtime(timezone.now()).strftime("%d/%m/%Y %H:%M")} '
        f'por {request.user.get_full_name() or request.user.username} — SENA Sistema de Gestión de Maquinaria v2.0</font>',
        styles['Normal']))

    doc.build(story)
    buf.seek(0)
    response = HttpResponse(buf.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Reporte_Alerta_{alerta.pk}_{alerta.maquina.codigo_inventario}.pdf"'
    return response


@login_required
def detalle_alerta_view(request, pk):
    """Detalle de alerta específica"""
    from usuarios.models import Usuario
    alerta = get_object_or_404(AlertaMaquina, pk=pk)

    # Técnicos disponibles para asignar (Personal de Mantenimiento activos)
    tecnicos = Usuario.objects.filter(
        cargo='Personal de Mantenimiento',
        estado='activo'
    ).order_by('nombres', 'apellidos')

    # Manejo de asignación de técnico vía POST
    if request.method == 'POST' and 'asignar_tecnico' in request.POST:
        tecnico_id = request.POST.get('tecnico_id')
        if tecnico_id:
            alerta.tecnico_asignado = get_object_or_404(Usuario, pk=tecnico_id)
            alerta.save(update_fields=['tecnico_asignado'])

    context = {
        'title': f'Alerta - {alerta.maquina.codigo_inventario}',
        'alerta': alerta,
        'tecnicos': tecnicos,
    }

    return render(request, 'maquinaria/detalle_alerta.html', context)

# Mantenimiento
@login_required
def mantenimiento_dashboard_view(request):
    """Dashboard de mantenimiento con datos reales"""
    from datetime import date, timedelta

    # Estadísticas de mantenimiento programado
    hoy = timezone.now().date()
    esta_semana = hoy + timedelta(days=7)

    # Mantenimientos programados para hoy
    mantenimientos_hoy = MantenimientoProgramado.objects.filter(
        fecha_programada__date=hoy,
        estado='programado'
    ).count()

    # Mantenimientos pendientes esta semana
    mantenimientos_pendientes = MantenimientoProgramado.objects.filter(
        fecha_programada__date__lte=esta_semana,
        fecha_programada__date__gte=hoy,
        estado='programado'
    ).count()

    # Mantenimientos vencidos
    mantenimientos_vencidos = MantenimientoProgramado.objects.filter(
        fecha_programada__date__lt=hoy,
        estado='programado'
    ).count()

    # Actividades recientes de mantenimiento
    actividades_mantenimiento = HistorialMaquina.objects.filter(
        tipo_evento__in=['mantenimiento', 'reparacion']
    ).select_related('maquina', 'usuario').order_by('-fecha_evento')[:10]

    # Mantenimientos programados próximos (usando el nuevo modelo)
    mantenimientos_proximos = MantenimientoProgramado.objects.filter(
        fecha_programada__date__lte=hoy + timedelta(days=7),
        fecha_programada__date__gte=hoy,
        estado='programado'
    ).select_related('maquina', 'tecnico_asignado').order_by('fecha_programada')[:10]

    # KPIs básicos de mantenimiento
    total_mantenimientos_programados = MantenimientoProgramado.objects.filter(
        estado__in=['programado', 'en_progreso']
    ).count()

    if total_mantenimientos_programados > 0:
        mantenimientos_al_dia = total_mantenimientos_programados - mantenimientos_vencidos
        cumplimiento_porcentaje = round((mantenimientos_al_dia / total_mantenimientos_programados * 100), 1)
    else:
        cumplimiento_porcentaje = 100.0

    # Filtros GET para la tabla principal
    estado_filtro   = request.GET.get('estado', '')
    tipo_filtro     = request.GET.get('tipo', '')
    prioridad_filtro = request.GET.get('prioridad', '')

    qs = MantenimientoProgramado.objects.select_related('maquina', 'tecnico_asignado').order_by('fecha_programada')
    if estado_filtro:
        qs = qs.filter(estado=estado_filtro)
    if tipo_filtro:
        qs = qs.filter(tipo=tipo_filtro)
    if prioridad_filtro:
        qs = qs.filter(prioridad=prioridad_filtro)

    from django.core.paginator import Paginator
    paginator = Paginator(qs, 15)
    mantenimientos_tabla = paginator.get_page(request.GET.get('page'))

    context = {
        'title': 'Panel de Mantenimiento',
        'mantenimientos_hoy': mantenimientos_hoy,
        'mantenimientos_pendientes': mantenimientos_pendientes,
        'mantenimientos_vencidos': mantenimientos_vencidos,
        'cumplimiento_porcentaje': cumplimiento_porcentaje,
        'mantenimientos_tabla': mantenimientos_tabla,
        'estado_filtro': estado_filtro,
        'tipo_filtro': tipo_filtro,
        'prioridad_filtro': prioridad_filtro,
    }

    return render(request, 'maquinaria/mantenimiento_dashboard.html', context)

@login_required
def programar_mantenimiento_view(request, pk=None):
    """Programar nuevo mantenimiento con datos reales"""
    import json
    from datetime import timedelta

    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            maquina_id = request.POST.get('maquina')
            tipo = request.POST.get('tipo', 'preventivo')
            titulo = request.POST.get('titulo')
            descripcion = request.POST.get('descripcion')
            prioridad = request.POST.get('prioridad', 'media')
            fecha_programada = request.POST.get('fecha_programada')
            duracion_estimada = request.POST.get('duracion_estimada', '02:00:00')  # Default 2 horas
            tecnico_asignado_id = request.POST.get('personal_asignado')
            personal_adicional_ids = request.POST.getlist('personal_adicional_ids')

            # Obtener listas de componentes, herramientas y repuestos
            componentes = request.POST.getlist('componentes')
            herramientas = request.POST.getlist('herramientas')
            repuestos = request.POST.getlist('repuestos')
            procedimientos = request.POST.get('procedimientos', '')
            costo_estimado = request.POST.get('costo_estimado')

            # Validar datos requeridos
            if not all([maquina_id, titulo, descripcion, fecha_programada]):
                messages.error(request, 'Por favor complete todos los campos requeridos.')
                return redirect('maquinaria:programar_mantenimiento')

            # Obtener la máquina
            try:
                maquina = Maquina.objects.get(pk=maquina_id)
            except Maquina.DoesNotExist:
                messages.error(request, 'La máquina seleccionada no existe.')
                return redirect('maquinaria:programar_mantenimiento')

            # Obtener técnico si fue asignado
            tecnico_asignado = None
            if tecnico_asignado_id:
                try:
                    tecnico_asignado = Usuario.objects.get(pk=tecnico_asignado_id)
                except Usuario.DoesNotExist:
                    pass

            # Convertir duración estimada
            try:
                horas, minutos, segundos = duracion_estimada.split(':')
                duracion_td = timedelta(hours=int(horas), minutes=int(minutos), seconds=int(segundos))
            except:
                duracion_td = timedelta(hours=2)  # Default 2 horas

            # Crear el mantenimiento programado
            mantenimiento = MantenimientoProgramado.objects.create(
                maquina=maquina,
                tipo=tipo,
                titulo=titulo,
                descripcion=descripcion,
                prioridad=prioridad,
                fecha_programada=fecha_programada,
                duracion_estimada=duracion_td,
                tecnico_asignado=tecnico_asignado,
                componentes_revisar=componentes,
                herramientas_necesarias=herramientas,
                repuestos_necesarios=repuestos,
                procedimientos=procedimientos,
                costo_estimado=float(costo_estimado) if costo_estimado else None
            )

            # Personal adicional
            if personal_adicional_ids:
                adicionales = Usuario.objects.filter(pk__in=personal_adicional_ids)
                mantenimiento.personal_adicional.set(adicionales)

            # Obtener usuario creador
            try:
                usuario = Usuario.objects.get(numero_documento=request.user.username)
                mantenimiento.created_by = usuario
                mantenimiento.save()
            except Usuario.DoesNotExist:
                pass

            # Crear entrada en el historial
            HistorialMaquina.objects.create(
                maquina=maquina,
                tipo_evento='mantenimiento',
                descripcion=f'Mantenimiento programado: {titulo} para {fecha_programada}',
                usuario=mantenimiento.created_by
            )

            messages.success(request, f'Mantenimiento "{titulo}" programado exitosamente para {maquina.codigo_inventario}')
            return redirect('maquinaria:mantenimiento_dashboard')

        except Exception as e:
            messages.error(request, f'Error al programar el mantenimiento: {str(e)}')
            return redirect('maquinaria:programar_mantenimiento')

    # GET request - mostrar formulario
    maquina_seleccionada = None
    if pk:
        try:
            maquina_seleccionada = Maquina.objects.get(pk=pk)
        except Maquina.DoesNotExist:
            pass

    try:
        usuarios_tecnicos = Usuario.objects.all().order_by('nombres', 'apellidos')[:20]
    except Exception:
        usuarios_tecnicos = []

    context = {
        'title': 'Programar Mantenimiento',
        'maquinas': Maquina.objects.select_related('categoria').all().order_by('codigo_inventario'),
        'maquina_seleccionada': maquina_seleccionada,
        'usuarios_tecnicos': usuarios_tecnicos,
    }

    return render(request, 'maquinaria/programar_mantenimiento.html', context)

# Importar/Exportar
@login_required
def importar_maquinas_view(request):
    return render(request, 'maquinaria/importar_maquinas.html', {'title': 'Importar Máquinas'})

@login_required
def exportar_maquinas_view(request):
    return render(request, 'maquinaria/exportar_maquinas.html', {'title': 'Exportar Máquinas'})

# QR Codes
@login_required
def generar_qr_maquina(request, pk):
    import qrcode
    import io

    maquina = get_object_or_404(Maquina, pk=pk)
    url = request.build_absolute_uri(
        reverse('maquinaria:info_qr', kwargs={'codigo': maquina.codigo_inventario})
    )

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='image/png')
    response['Content-Disposition'] = f'inline; filename="QR_{maquina.codigo_inventario}.png"'
    return response

@login_required
def info_qr_maquina(request, codigo):
    maquina = get_object_or_404(Maquina, codigo_inventario=codigo)
    historial = HistorialMaquina.objects.filter(maquina=maquina).order_by('-fecha_evento')[:5]
    context = {
        'title': f'Info QR - {maquina.codigo_inventario}',
        'maquina': maquina,
        'historial': historial,
    }
    return render(request, 'maquinaria/info_qr.html', context)

# API endpoints para AJAX
@login_required
def buscar_maquinas_api(request):
    return JsonResponse({'results': []})

@login_required
def estadisticas_maquinaria_api(request):
    return JsonResponse({'stats': {}})

@login_required
def alertas_activas_api(request):
    return JsonResponse({'alertas': []})

@login_required
def datos_maquina_api(request, pk):
    return JsonResponse({'data': {}})


# ==================== OBJETOS / PIEZAS ====================

@login_required
def registrar_objeto_view(request):
    """Registrar un nuevo objeto/pieza con fotos desde múltiples ángulos"""
    from .forms import ObjetoMaquinariaForm
    from .models import ObjetoMaquinaria
    import base64
    from django.core.files.base import ContentFile

    if request.method == 'POST':
        form = ObjetoMaquinariaForm(request.POST, request.FILES)
        if form.is_valid():
            objeto = form.save(commit=False)

            # Asignar usuario creador
            try:
                usuario = Usuario.objects.get(numero_documento=request.user.username)
                objeto.created_by = usuario
            except Usuario.DoesNotExist:
                pass

            # Procesar fotos capturadas por webcam (base64)
            campos_foto = [
                'foto_frontal', 'foto_lateral_derecha', 'foto_lateral_izquierda',
                'foto_trasera', 'foto_superior', 'foto_inferior'
            ]
            for campo in campos_foto:
                b64_data = request.POST.get(f'{campo}_base64', '')
                if b64_data and b64_data.startswith('data:image'):
                    # Extraer datos base64 (eliminar header "data:image/png;base64,")
                    try:
                        header, imgstr = b64_data.split(';base64,')
                        ext = header.split('/')[-1]
                        filename = f'{campo}_{objeto.nombre[:20].replace(" ", "_")}.{ext}'
                        setattr(objeto, campo, ContentFile(
                            base64.b64decode(imgstr), name=filename
                        ))
                    except Exception:
                        pass

            objeto.save()

            # Registrar en historial si tiene máquina asociada
            if objeto.maquina:
                HistorialMaquina.objects.create(
                    maquina=objeto.maquina,
                    tipo_evento='actualizacion',
                    descripcion=f'Objeto/pieza registrado: {objeto.nombre}',
                    usuario=objeto.created_by
                )

            messages.success(request, f'Objeto "{objeto.nombre}" registrado exitosamente con {objeto.total_fotos} foto(s)')
            return redirect('maquinaria:detalle_objeto', pk=objeto.pk)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = ObjetoMaquinariaForm()

    foto_campos = [
        ('foto_frontal', 'Frontal'),
        ('foto_lateral_derecha', 'Lateral Derecha'),
        ('foto_lateral_izquierda', 'Lateral Izquierda'),
        ('foto_trasera', 'Trasera'),
        ('foto_superior', 'Superior'),
        ('foto_inferior', 'Inferior'),
    ]
    context = {
        'title': 'Registrar Objeto/Pieza',
        'form': form,
        'foto_campos': foto_campos,
    }
    return render(request, 'maquinaria/registrar_objeto.html', context)


@login_required
def lista_objetos_view(request):
    """Lista todos los objetos/piezas registrados"""
    from .models import ObjetoMaquinaria

    objetos_list = ObjetoMaquinaria.objects.select_related('maquina').all()

    # Filtros
    estado_filtro = request.GET.get('estado')
    busqueda = request.GET.get('busqueda')
    maquina_filtro = request.GET.get('maquina')

    if estado_filtro:
        objetos_list = objetos_list.filter(estado=estado_filtro)
    if maquina_filtro:
        objetos_list = objetos_list.filter(maquina_id=maquina_filtro)
    if busqueda:
        objetos_list = objetos_list.filter(
            Q(nombre__icontains=busqueda) |
            Q(modelo__icontains=busqueda) |
            Q(serie__icontains=busqueda) |
            Q(fabricante__icontains=busqueda)
        )

    paginator = Paginator(objetos_list, 20)
    page = request.GET.get('page')
    objetos = paginator.get_page(page)

    context = {
        'title': 'Objetos y Piezas',
        'objetos': objetos,
        'estado_filtro': estado_filtro,
        'busqueda': busqueda,
        'maquina_filtro': maquina_filtro,
        'maquinas': Maquina.objects.all().order_by('codigo_inventario'),
    }
    return render(request, 'maquinaria/lista_objetos.html', context)


@login_required
def detalle_objeto_view(request, pk):
    """Detalle de un objeto/pieza"""
    from .models import ObjetoMaquinaria

    objeto = get_object_or_404(ObjetoMaquinaria, pk=pk)

    context = {
        'title': f'Objeto - {objeto.nombre}',
        'objeto': objeto,
    }
    return render(request, 'maquinaria/detalle_objeto.html', context)


@login_required
def editar_objeto_view(request, pk):
    """Editar un objeto/pieza existente"""
    from .forms import ObjetoMaquinariaForm
    from .models import ObjetoMaquinaria
    import base64
    from django.core.files.base import ContentFile

    objeto = get_object_or_404(ObjetoMaquinaria, pk=pk)

    if request.method == 'POST':
        form = ObjetoMaquinariaForm(request.POST, request.FILES, instance=objeto)
        if form.is_valid():
            obj = form.save(commit=False)

            campos_foto = [
                'foto_frontal', 'foto_lateral_derecha', 'foto_lateral_izquierda',
                'foto_trasera', 'foto_superior', 'foto_inferior'
            ]
            for campo in campos_foto:
                b64_data = request.POST.get(f'{campo}_base64', '')
                if b64_data and b64_data.startswith('data:image'):
                    try:
                        header, imgstr = b64_data.split(';base64,')
                        ext = header.split('/')[-1]
                        filename = f'{campo}_{obj.nombre[:20].replace(" ", "_")}.{ext}'
                        setattr(obj, campo, ContentFile(
                            base64.b64decode(imgstr), name=filename
                        ))
                    except Exception:
                        pass

            obj.save()
            messages.success(request, f'Objeto "{obj.nombre}" actualizado exitosamente')
            return redirect('maquinaria:detalle_objeto', pk=pk)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = ObjetoMaquinariaForm(instance=objeto)

    foto_campos = [
        ('foto_frontal', 'Frontal'),
        ('foto_lateral_derecha', 'Lateral Derecha'),
        ('foto_lateral_izquierda', 'Lateral Izquierda'),
        ('foto_trasera', 'Trasera'),
        ('foto_superior', 'Superior'),
        ('foto_inferior', 'Inferior'),
    ]
    # Build photo URLs for existing photos
    fotos_existentes = {}
    for campo, _ in foto_campos:
        foto = getattr(objeto, campo)
        if foto:
            fotos_existentes[campo] = foto.url

    context = {
        'title': f'Editar - {objeto.nombre}',
        'form': form,
        'objeto': objeto,
        'foto_campos': foto_campos,
        'fotos_existentes': fotos_existentes,
    }
    return render(request, 'maquinaria/registrar_objeto.html', context)


@login_required
def eliminar_objeto_view(request, pk):
    """Eliminar un objeto/pieza"""
    from .models import ObjetoMaquinaria

    objeto = get_object_or_404(ObjetoMaquinaria, pk=pk)

    if request.method == 'POST':
        nombre = objeto.nombre
        objeto.delete()
        messages.success(request, f'Objeto "{nombre}" eliminado exitosamente')
        return redirect('maquinaria:lista_objetos')

    context = {
        'title': f'Eliminar - {objeto.nombre}',
        'objeto': objeto,
    }
    return render(request, 'maquinaria/eliminar_objeto.html', context)


# ── Uso de Maquinaria ────────────────────────────────────────────────────────

@login_required
def registrar_uso_maquinaria_view(request):
    """Registrar una nueva sesión de uso de maquinaria."""
    maquina_pk = request.GET.get('maquina')
    initial = {}
    if maquina_pk:
        try:
            maq = Maquina.objects.get(pk=maquina_pk)
            initial['maquina'] = maq
            initial['horas_totales_maquina'] = maq.horas_uso_total
        except Maquina.DoesNotExist:
            pass

    form = UsoMaquinariaForm(initial=initial)

    if request.method == 'POST':
        form = UsoMaquinariaForm(request.POST)
        if form.is_valid():
            uso = form.save(commit=False)
            try:
                uso.registrado_por = Usuario.objects.get(numero_documento=request.user.username)
            except Exception:
                pass
            uso.save()

            # Actualizar horas totales de la máquina
            maq = uso.maquina
            maq.horas_uso_total = uso.horas_totales_maquina
            maq.save(update_fields=['horas_uso_total'])

            messages.success(request, f'Uso de "{maq.nombre}" registrado correctamente.')
            return redirect('maquinaria:lista_uso_maquinaria')

    return render(request, 'maquinaria/uso_maquinaria.html', {
        'title': 'Registrar Uso de Maquinaria',
        'form': form,
    })


@login_required
def lista_uso_maquinaria_view(request):
    """Lista todos los registros de uso de maquinaria."""
    registros = UsoMaquinaria.objects.select_related(
        'maquina', 'instructor_encargado', 'registrado_por'
    ).all()

    q = request.GET.get('q', '').strip()
    if q:
        registros = registros.filter(
            Q(maquina__nombre__icontains=q) |
            Q(maquina__codigo_inventario__icontains=q) |
            Q(ficha__icontains=q)
        )

    maquina_filtro = request.GET.get('maquina', '')
    if maquina_filtro:
        registros = registros.filter(maquina_id=maquina_filtro)

    paginator = Paginator(registros, 20)
    page = request.GET.get('page')
    registros_page = paginator.get_page(page)

    return render(request, 'maquinaria/lista_uso_maquinaria.html', {
        'title': 'Registros de Uso de Maquinaria',
        'registros': registros_page,
        'q': q,
        'maquinas': Maquina.objects.all().order_by('codigo_inventario'),
        'maquina_filtro': maquina_filtro,
    })


@login_required
def mantenimientos_maquina_view(request, pk):
    """Lista todos los mantenimientos de una máquina específica."""
    maquina = get_object_or_404(Maquina, pk=pk)

    mantenimientos = MantenimientoProgramado.objects.filter(
        maquina=maquina
    ).select_related('tecnico_asignado', 'tecnico_realizado').order_by('-fecha_programada')

    # Filtro por estado
    estado_filtro = request.GET.get('estado', '')
    if estado_filtro:
        mantenimientos = mantenimientos.filter(estado=estado_filtro)

    # Filtro por tipo
    tipo_filtro = request.GET.get('tipo', '')
    if tipo_filtro:
        mantenimientos = mantenimientos.filter(tipo=tipo_filtro)

    paginator = Paginator(mantenimientos, 15)
    page = request.GET.get('page')
    mantenimientos_page = paginator.get_page(page)

    # Totales para resumen
    total = MantenimientoProgramado.objects.filter(maquina=maquina)
    resumen = {
        'total': total.count(),
        'completados': total.filter(estado='completado').count(),
        'programados': total.filter(estado='programado').count(),
        'en_progreso': total.filter(estado='en_progreso').count(),
        'cancelados': total.filter(estado='cancelado').count(),
    }

    return render(request, 'maquinaria/mantenimientos_maquina.html', {
        'title': f'Mantenimientos - {maquina.codigo_inventario}',
        'maquina': maquina,
        'mantenimientos': mantenimientos_page,
        'estado_filtro': estado_filtro,
        'tipo_filtro': tipo_filtro,
        'resumen': resumen,
        'estado_choices': MantenimientoProgramado.ESTADO_CHOICES,
        'tipo_choices': MantenimientoProgramado.TIPO_MANTENIMIENTO_CHOICES,
    })
