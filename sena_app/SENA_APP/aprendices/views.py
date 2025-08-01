from django.http import HttpResponse
from django.template import loader
from .models import Aprendiz, Curso

# Create your views here.
def aprendices(request):
    lista_aprendices = Aprendiz.objects.all().order_by('apellido', 'nombre')
    template = loader.get_template('lista_aprendices.html')
    context = {
        'lista_aprendices': lista_aprendices,
        'total_aprendices': lista_aprendices.count(),
    }
    return HttpResponse(template.render(context, request))

def inicio(request):
    total_aprendices = Aprendiz.objects.count()
    total_cursos = Curso.objects.count()
    cursos_activos = Curso.objects.filter(estado__in=['INI', 'EJE']).count()
    template = loader.get_template('inicio.html')
    
    context = {
        'total_aprendices': total_aprendices,
        'total_cursos': total_cursos,
        'cursos_activos': cursos_activos,
    }
    return HttpResponse(template.render(context, request))
