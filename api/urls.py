


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'maquinas', views.MaquinaViewSet, basename='maquina')
router.register(r'alertas', views.AlertaMaquinaViewSet, basename='alerta')

app_name = 'api'

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # Authentication
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
    path('auth/login/', views.LoginAPIView.as_view(), name='api_login'),
    path('auth/logout/', views.LogoutAPIView.as_view(), name='api_logout'),

    # Machinery endpoints
    path('maquinas/buscar/', views.BuscarMaquinasAPIView.as_view(), name='buscar_maquinas'),
    path('maquinas/<int:pk>/historial/', views.HistorialMaquinaAPIView.as_view(), name='historial_maquina'),
    path('maquinas/<int:pk>/cambiar-estado/', views.CambiarEstadoMaquinaAPIView.as_view(), name='cambiar_estado_maquina'),

    # Alerts endpoints
    path('alertas/activas/', views.AlertasActivasAPIView.as_view(), name='alertas_activas'),
    path('alertas/<int:pk>/resolver/', views.ResolverAlertaAPIView.as_view(), name='resolver_alerta'),

    # Reports endpoints
    path('reportes/generar/', views.GenerarReporteAPIView.as_view(), name='generar_reporte'),
    path('reportes/<uuid:pk>/descargar/', views.DescargarReporteAPIView.as_view(), name='descargar_reporte'),

    # Dashboard and metrics
    path('dashboard/datos/', views.DatosDashboardAPIView.as_view(), name='datos_dashboard'),
    path('metricas/resumen/', views.ResumenMetricasAPIView.as_view(), name='resumen_metricas'),
    path('estadisticas/generales/', views.EstadisticasGeneralesAPIView.as_view(), name='estadisticas_generales'),

    # Status endpoint
    path('status/', views.SystemStatusAPIView.as_view(), name='system_status'),

    # Bulk operations
    path('bulk/importar-maquinas/', views.ImportarMaquinasAPIView.as_view(), name='importar_maquinas'),
    path('bulk/exportar-maquinas/', views.ExportarMaquinasAPIView.as_view(), name='exportar_maquinas'),
]