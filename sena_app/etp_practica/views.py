from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Empresa, EtapaPractica
from .forms import EmpresaForm, EtapaPracticaForm

def lista_empresas(request):
    empresas = Empresa.objects.all()
    total_empresas = empresas.count()
    
    context = {
        'empresas': empresas,
        'total_empresas': total_empresas,
    }
    return render(request, 'etp_practica/lista_empresas.html', context)

def detalle_empresa(request, empresa_id):
    empresa = Empresa.objects.get(id=empresa_id)
    stats = {
        'total': EtapaPractica.objects.filter(empresa=empresa).count(),
        'activos': EtapaPractica.objects.filter(empresa=empresa, estado='PRODUCTIVA').count(),
        'finalizados': EtapaPractica.objects.filter(empresa=empresa, estado='FINALIZADO').count(),
        'retirados': EtapaPractica.objects.filter(empresa=empresa, estado='RETIRADO').count(),
    }
    return render(request, 'detalle_empresaS.html', {'empresa': empresa, 'stats': stats})

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

def crear_empresa(request):
    if request.method == 'POST':
        form = EmpresaForm(request.POST)
        if form.is_valid():
            empresa = form.save()
            messages.success(request, 'Empresa creada exitosamente')
            return redirect('etp_practica:detalle_empresa', empresa_id=empresa.id)
    else:
        form = EmpresaForm()
    
    return render(request, 'etp_practica/crear_empresa.html', {'form': form})

def editar_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    
    if request.method == 'POST':
        form = EmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empresa actualizada exitosamente')
            return redirect('etp_practica:detalle_empresa', empresa_id=empresa.id)
    else:
        form = EmpresaForm(instance=empresa)
    
    return render(request, 'etp_practica/editar_empresa.html', {'form': form, 'empresa': empresa})

def crear_etapa(request):
    if request.method == 'POST':
        form = EtapaPracticaForm(request.POST)
        if form.is_valid():
            etapa = form.save()
            messages.success(request, 'Etapa de práctica creada exitosamente')
            return redirect('etp_practica:detalle_bitacora', etapa_id=etapa.id)
    else:
        form = EtapaPracticaForm()
    
    return render(request, 'etp_practica/crear_etapa.html', {'form': form})

def editar_etapa(request, etapa_id):
    etapa = get_object_or_404(EtapaPractica, id=etapa_id)
    
    if request.method == 'POST':
        form = EtapaPracticaForm(request.POST, instance=etapa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Etapa actualizada exitosamente')
            return redirect('etp_practica:detalle_bitacora', etapa_id=etapa.id)
    else:
        form = EtapaPracticaForm(instance=etapa)
    
    return render(request, 'etp_practica/editar_etapa.html', {'form': form, 'etapa': etapa})