from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('',              views.dashboard_inventario_view, name='dashboard'),
    path('nueva/',        views.nueva_pieza_view,          name='nueva_pieza'),
    path('lista/',        views.lista_piezas_view,         name='lista_piezas'),
    path('<int:pk>/',     views.detalle_pieza_view,        name='detalle_pieza'),
    path('<int:pk>/editar/',   views.editar_pieza_view,   name='editar_pieza'),
    path('<int:pk>/eliminar/', views.eliminar_pieza_view, name='eliminar_pieza'),
]
