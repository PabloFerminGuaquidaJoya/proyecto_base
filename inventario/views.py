from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q

from .models import PiezaInventario
from .forms import PiezaInventarioForm
from usuarios.models import Usuario


@login_required
def dashboard_inventario_view(request):
    total     = PiezaInventario.objects.count()
    usadas    = PiezaInventario.objects.filter(condicion='usada').count()
    cambiadas = PiezaInventario.objects.filter(condicion='cambiada').count()
    alertas   = sum(1 for p in PiezaInventario.objects.all() if p.tiene_alerta)
    recientes = PiezaInventario.objects.order_by('-fecha_registro')[:5]

    return render(request, 'inventario/dashboard_inventario.html', {
        'title':           'Inventario - SENA',
        'total_piezas':    total,
        'piezas_usadas':   usadas,
        'piezas_cambiadas': cambiadas,
        'alertas_activas': alertas,
        'recientes':       recientes,
        'usuarios_activos': Usuario.objects.filter(estado='activo').order_by('nombres'),
    })


@login_required
def nueva_pieza_view(request):
    form = PiezaInventarioForm()
    if request.method == 'POST':
        form = PiezaInventarioForm(request.POST, request.FILES)
        if form.is_valid():
            pieza = form.save(commit=False)
            try:
                from usuarios.models import Usuario
                pieza.registrado_por = Usuario.objects.get(numero_documento=request.user.username)
            except Exception:
                pass
            pieza.save()
            messages.success(request, f'Pieza "{pieza.nombre}" registrada correctamente.')
            return redirect('inventario:lista_piezas')

    return render(request, 'inventario/nueva_pieza.html', {
        'title': 'Nueva Pieza - SENA',
        'form': form,
    })


@login_required
def lista_piezas_view(request):
    piezas = PiezaInventario.objects.all().order_by('-fecha_registro')

    # Filtro por búsqueda
    q = request.GET.get('q', '').strip()
    if q:
        piezas = piezas.filter(
            Q(nombre__icontains=q) |
            Q(codigo_inventario__icontains=q) |
            Q(marca__icontains=q) |
            Q(categoria__icontains=q)
        )

    # Filtro por condición
    condicion = request.GET.get('condicion', '')
    if condicion:
        piezas = piezas.filter(condicion=condicion)

    return render(request, 'inventario/lista_piezas.html', {
        'title': 'Inventario - Todas las Piezas',
        'piezas': piezas,
        'q': q,
        'condicion_filtro': condicion,
        'condicion_choices': PiezaInventario.CONDICION_CHOICES,
    })


@login_required
def detalle_pieza_view(request, pk):
    pieza = get_object_or_404(PiezaInventario, pk=pk)
    return render(request, 'inventario/detalle_pieza.html', {
        'title': f'{pieza.nombre} - Inventario',
        'pieza': pieza,
    })


@login_required
def editar_pieza_view(request, pk):
    pieza = get_object_or_404(PiezaInventario, pk=pk)
    form  = PiezaInventarioForm(instance=pieza)
    if request.method == 'POST':
        form = PiezaInventarioForm(request.POST, request.FILES, instance=pieza)
        if form.is_valid():
            form.save()
            messages.success(request, f'Pieza "{pieza.nombre}" actualizada.')
            return redirect('inventario:detalle_pieza', pk=pieza.pk)

    return render(request, 'inventario/nueva_pieza.html', {
        'title': f'Editar {pieza.nombre}',
        'form': form,
        'editando': True,
        'pieza': pieza,
    })


@login_required
def eliminar_pieza_view(request, pk):
    pieza = get_object_or_404(PiezaInventario, pk=pk)
    if request.method == 'POST':
        nombre = pieza.nombre
        pieza.delete()
        messages.success(request, f'Pieza "{nombre}" eliminada.')
        return redirect('inventario:lista_piezas')
    return render(request, 'inventario/eliminar_pieza.html', {
        'title': f'Eliminar {pieza.nombre}',
        'pieza': pieza,
    })
