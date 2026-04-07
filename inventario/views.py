import base64
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.base import ContentFile
from django.db.models import Q

from .models import PiezaInventario
from .forms import PiezaInventarioForm
from usuarios.models import Usuario


FOTO_ANGULOS = [
    ('foto_frontal',           'Frontal'),
    ('foto_lateral_derecha',   'Lateral Derecha'),
    ('foto_lateral_izquierda', 'Lateral Izquierda'),
    ('foto_trasera',           'Trasera'),
    ('foto_superior',          'Superior'),
    ('foto_inferior',          'Inferior'),
]


def _guardar_base64(pieza, campo, data_url):
    """Convierte un dataURL base64 y lo guarda en el ImageField indicado."""
    if not data_url or not data_url.startswith('data:image'):
        return
    try:
        header, encoded = data_url.split(',', 1)
        imagen_bytes = base64.b64decode(encoded)
        nombre = f'{campo}_{uuid.uuid4().hex[:8]}.jpg'
        getattr(pieza, campo).save(nombre, ContentFile(imagen_bytes), save=False)
    except Exception:
        pass


@login_required
def dashboard_inventario_view(request):
    total     = PiezaInventario.objects.count()
    usadas    = PiezaInventario.objects.filter(condicion='usada').count()
    cambiadas = PiezaInventario.objects.filter(condicion='cambiada').count()
    alertas   = sum(1 for p in PiezaInventario.objects.all() if p.tiene_alerta)

    # Lista completa con filtros (igual que lista_piezas_view)
    piezas = PiezaInventario.objects.all().order_by('-fecha_registro')

    q = request.GET.get('q', '').strip()
    if q:
        piezas = piezas.filter(
            Q(nombre__icontains=q) |
            Q(codigo_inventario__icontains=q) |
            Q(marca__icontains=q) |
            Q(categoria__icontains=q)
        )

    condicion = request.GET.get('condicion', '')
    if condicion:
        piezas = piezas.filter(condicion=condicion)

    return render(request, 'inventario/dashboard_inventario.html', {
        'title':            'Inventario - SENA',
        'total_piezas':     total,
        'piezas_usadas':    usadas,
        'piezas_cambiadas': cambiadas,
        'alertas_activas':  alertas,
        'piezas':           piezas,
        'q':                q,
        'condicion_filtro': condicion,
        'condicion_choices': PiezaInventario.CONDICION_CHOICES,
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
                pieza.registrado_por = Usuario.objects.get(numero_documento=request.user.username)
            except Exception:
                pass
            pieza.save()
            # Guardar imágenes base64 de la cámara web (6 ángulos)
            fotos_capturadas = 0
            for campo, _ in FOTO_ANGULOS:
                data_url = request.POST.get(f'{campo}_data', '')
                if data_url:
                    _guardar_base64(pieza, campo, data_url)
                    fotos_capturadas += 1
            if fotos_capturadas:
                pieza.save()
            messages.success(
                request,
                f'"{pieza.nombre}" registrado correctamente'
                + (f' con {fotos_capturadas} foto(s) de ángulos.' if fotos_capturadas else '.')
            )
            return redirect('inventario:lista_piezas')

    return render(request, 'inventario/nueva_pieza.html', {
        'title': 'Registrar Pieza/Objeto - SENA',
        'form': form,
        'foto_angulos': FOTO_ANGULOS,
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
        'foto_angulos': FOTO_ANGULOS,
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
