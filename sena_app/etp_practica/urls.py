from django.urls import path
from . import views

app_name = 'etp_practica'

urlpatterns = [
    path('', views.lista_empresas, name='lista_empresas'),
    path('empresa/<int:empresa_id>/', views.detalle_empresa, name='detalle_empresa'),
    path('empresa/nueva/', views.crear_empresa, name='crear_empresa'),
    path('empresa/<int:empresa_id>/editar/', views.editar_empresa, name='editar_empresa'),
    path('empresa/<int:empresa_id>/eliminar/', views.eliminar_empresa, name='eliminar_empresa'),
    path('empresa/<int:empresa_id>/aprendices/', views.aprendices_asignados, name='aprendices_asignados'),
    path('empresa/<int:empresa_id>/bitacoras/', views.bitacoras, name='bitacoras'),
    path('empresa/<int:empresa_id>/asignar-aprendiz/', views.asignar_aprendiz, name='asignar_aprendiz'),
    path('asignaciones/', views.gestionar_asignaciones, name='gestionar_asignaciones'),
    path('empresa/<int:empresa_id>/asignaciones/', views.gestionar_asignaciones, name='asignaciones_empresa'),
    path('asignacion/<int:asignacion_id>/', views.detalle_asignacion, name='detalle_asignacion'),
    path('asignacion/<int:asignacion_id>/editar/', views.editar_asignacion, name='editar_asignacion'),
    path('asignacion/<int:asignacion_id>/confirmar/', views.confirmar_asignacion, name='confirmar_asignacion'),
    path('asignacion/<int:asignacion_id>/cancelar/', views.cancelar_asignacion, name='cancelar_asignacion'),
    path('asignacion/<int:asignacion_id>/iniciar-practica/', views.iniciar_etapa_practica, name='iniciar_etapa_practica'),
    path('bitacora/<int:etapa_id>/', views.detalle_bitacora, name='detalle_bitacora'),
    path('api/aprendices-disponibles/', views.api_aprendices_disponibles, name='api_aprendices_disponibles'),
    path('api/empresa/<int:empresa_id>/estadisticas/', views.api_estadisticas_empresa, name='api_estadisticas_empresa'),
]