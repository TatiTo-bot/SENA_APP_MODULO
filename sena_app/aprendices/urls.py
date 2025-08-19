from django.urls import path
from . import views
from .views import AprendizFormView

app_name = 'aprendices'

urlpatterns = [
    path('aprendices/aprendiz/<int:aprendiz_id>', views.detalle_aprendiz, name='detalle_aprendiz'),
    path('aprendices/', views.aprendices, name='lista_aprendices'),
    path('cursos/curso/<int:curso_id>', views.detalle_curso, name='detalle_curso'),
    path('cursos/', views.lista_cursos, name='lista_cursos'),
    path('crear_aprendiz/', AprendizFormView.as_view(), name='crear_aprendiz'),
    path('', views.inicio, name='inicio'),
]