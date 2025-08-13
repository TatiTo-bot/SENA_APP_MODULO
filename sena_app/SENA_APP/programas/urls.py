from django.urls import path
from . import views
from .views import ProgramaFormView

app_name = 'programas'

urlpatterns = [
    path('programas/', views.programas, name='lista_programas'),
    path('programas/programa/<int:programa_id>/', views.detalle_programa, name='detalle_programa'),
    path('crear_programa/', ProgramaFormView.as_view(), name='crear_programa_form'),
]