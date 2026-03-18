from django.urls import path
from . import views

app_name = 'vision'

urlpatterns = [
    path('api/detectar/', views.detectar_view, name='detectar'),
    path('api/estado/',   views.estado_view,   name='estado'),
]
