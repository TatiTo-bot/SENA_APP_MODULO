from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .models import Empresa, EtapaPractica
from .forms import EmpresaForm
from django.urls import reverse

@csrf_protect
def crear_empresa(request):
    if request.method == 'POST':
        form = EmpresaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Empresa registrada exitosamente!')
            return redirect(reverse('etp_practica:lista_empresas'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
    else:
        form = EmpresaForm()
        
    return render(request, 'etp_practica/crear_empresa.html', {'form': form})
def lista_empresas(request):
    empresas = Empresa.objects.all()
    return render(request, 'etp_practica/lista_empresas.html', {
        'lista_empresas': empresas,
        'total_empresas': empresas.count()
    })
    
def detalle_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, pk=empresa_id)
    stats = {
        'total': EtapaPractica.objects.filter(empresa=empresa).count(),
        'activos': EtapaPractica.objects.filter(empresa=empresa, estado='PRODUCTIVA').count(),
        'finalizados': EtapaPractica.objects.filter(empresa=empresa, estado='FINALIZADO').count(),
        'retirados': EtapaPractica.objects.filter(empresa=empresa, estado='RETIRADO').count(),
    }
    return render(request, 'etp_practica/detalle_empresas.html', {'empresa': empresa, 'stats': stats})

def aprendices_asignados(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    etapas = EtapaPractica.objects.filter(empresa=empresa)
    
    total_aprendices = etapas.count()
    con_alertas = etapas.filter(estado__in=['APLAZADO', 'RETIRADO']).count()
    finalizados = etapas.filter(estado='FINALIZADO').count()
    
    context = {
        'empresa': empresa,
        'etapas': etapas,
        'total_aprendices': total_aprendices,
        'con_alertas': con_alertas,
        'finalizados': finalizados,
    }
    return render(request, 'etp_practica/aprendices_asignados.html', context)

def bitacoras(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    etapas = EtapaPractica.objects.filter(empresa=empresa)
    
    sin_iniciar = etapas.filter(estado='LECTIVA').count()
    desertaron = etapas.filter(estado='RETIRADO').count()
    enviadas = etapas.filter(estado='PRODUCTIVA').count()
    revisadas = etapas.filter(estado='FINALIZADO').count()
    con_observaciones = etapas.filter(estado='APLAZADO').count()
    
    context = {
        'empresa': empresa,
        'etapas': etapas,
        'sin_iniciar': sin_iniciar,
        'desertaron': desertaron,
        'enviadas': enviadas,
        'revisadas': revisadas,
        'con_observaciones': con_observaciones,
    }
    return render(request, 'etp_practica/bitacoras.html', context)

def detalle_bitacora(request, etapa_id):
    etapa = get_object_or_404(EtapaPractica, id=etapa_id)
    
    context = {
        'etapa': etapa,
        'empresa': etapa.empresa,
        'aprendiz': etapa.aprendiz,
    }
    return render(request, 'etp_practica/detalle_bitacora.html', context)

@csrf_protect
def editar_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    
    if request.method == 'POST':
        form = EmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empresa actualizada exitosamente')
            return redirect('etp_practica:detalle_empresa', empresa_id=empresa.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
    else:
        form = EmpresaForm(instance=empresa)
    
    return render(request, 'etp_practica/editar_empresa.html', {'form': form, 'empresa': empresa})
