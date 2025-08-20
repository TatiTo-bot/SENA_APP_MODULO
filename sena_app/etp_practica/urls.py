from django.urls import path
from . import views

app_name = 'etp_practica'

urlpatterns = [
    path('', views.lista_empresas, name='lista_empresas'),
    path('empresa/<int:empresa_id>/', views.detalle_empresa, name='detalle_empresa'),
    path('empresa/nueva/', views.crear_empresa, name='crear_empresa'),    path('empresa/<int:empresa_id>/editar/', views.editar_empresa, name='editar_empresa'),
    path('empresa/<int:empresa_id>/aprendices/', views.aprendices_asignados, name='aprendices_asignados'),
    path('empresa/<int:empresa_id>/bitacoras/', views.bitacoras, name='bitacoras'),
]