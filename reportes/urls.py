from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    # Dashboard de reportes
    path('', views.dashboard_reportes_view, name='dashboard'),
    path('visual/', views.visual_dashboard_view, name='visual_dashboard'),

    # Generación de reportes
    path('generar/', views.generar_reporte_view, name='generar_reporte'),
    path('crear/', views.crear_reporte_web, name='crear_reporte_web'),
    path('api/crear/', views.crear_reporte_api, name='crear_reporte_api'),
    path('lista/', views.lista_reportes_view, name='lista_reportes'),
    path('detalle/<uuid:pk>/', views.detalle_reporte_view, name='detalle_reporte'),
    path('descargar/<uuid:pk>/', views.descargar_reporte, name='descargar_reporte'),
    path('cancelar/<uuid:pk>/', views.cancelar_reporte, name='cancelar_reporte'),

    # Tipos de reporte
    path('tipos/', views.tipos_reporte_view, name='tipos_reporte'),
    path('tipos/crear/', views.crear_tipo_reporte_view, name='crear_tipo_reporte'),

    # Métricas y KPIs
    path('metricas/', views.metricas_view, name='metricas'),
    path('kpis/', views.kpis_view, name='kpis'),
    path('eficiencia/', views.reporte_eficiencia_view, name='reporte_eficiencia'),
    path('costos/', views.reporte_costos_view, name='reporte_costos'),
    path('mantenimiento/', views.reporte_mantenimiento_view, name='reporte_mantenimiento'),

    # Análisis avanzados
    path('analisis/tendencias/', views.analisis_tendencias_view, name='analisis_tendencias'),
    path('analisis/predicciones/', views.analisis_predicciones_view, name='analisis_predicciones'),
    path('analisis/comparativo/', views.analisis_comparativo_view, name='analisis_comparativo'),

    # Exportaciones especializadas
    path('exportar/excel/', views.exportar_excel_view, name='exportar_excel'),
    path('exportar/pdf/', views.exportar_pdf_view, name='exportar_pdf'),
    path('exportar/csv/', views.exportar_csv_view, name='exportar_csv'),

    # API endpoints para widgets y gráficos
    path('api/widget/<int:widget_id>/datos/', views.datos_widget_api, name='api_datos_widget'),
    path('api/grafico/eficiencia/', views.grafico_eficiencia_api, name='api_grafico_eficiencia'),
    path('api/grafico/costos/', views.grafico_costos_api, name='api_grafico_costos'),
    path('api/grafico/estados/', views.grafico_estados_api, name='api_grafico_estados'),
    path('api/tabla/maquinas/', views.tabla_maquinas_api, name='api_tabla_maquinas'),

    # Dashboard personalizable
    path('dashboard/personalizar/', views.personalizar_dashboard_view, name='personalizar_dashboard'),
    path('dashboard/widget/agregar/', views.agregar_widget_dashboard, name='agregar_widget'),
    path('dashboard/widget/<int:pk>/eliminar/', views.eliminar_widget_dashboard, name='eliminar_widget'),

    # Vista previa de reporte
    path('api/preview/', views.preview_reporte_api, name='api_preview_reporte'),

    # API para filtros dinámicos
    path('api/filtros/centros/', views.filtros_centros_api, name='api_filtros_centros'),
    path('api/filtros/categorias/', views.filtros_categorias_api, name='api_filtros_categorias'),
    path('api/aplicar-filtros/', views.aplicar_filtros_api, name='api_aplicar_filtros'),

    # Programación de reportes automáticos
    path('programados/', views.reportes_programados_view, name='reportes_programados'),
    path('programados/crear/', views.crear_reporte_programado_view, name='crear_reporte_programado'),
]