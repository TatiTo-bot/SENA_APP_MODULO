from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.db import IntegrityError
from .models import Empresa, EtapaPractica
from .forms import EmpresaForm, EtapaPracticaForm
from django.urls import reverse

@csrf_protect
def crear_empresa(request):
    if request.method == 'POST':
        form = EmpresaForm(request.POST)
        if form.is_valid():
            try:
                empresa = form.save()
                messages.success(request, f'¡Empresa "{empresa.nombre}" registrada exitosamente!')
                return redirect(reverse('etp_practica:lista_empresas'))
            except IntegrityError as e:
                if 'nit' in str(e):
                    messages.error(request, 'Error: Ya existe una empresa con este NIT.')
                    form.add_error('nit', 'Ya existe una empresa con este NIT.')
                else:
                    messages.error(request, 'Error al guardar la empresa. Verifique que todos los datos sean únicos.')
            except Exception as e:
                messages.error(request, f'Error inesperado al registrar la empresa: {str(e)}')
        else:
            # Mostrar errores específicos del formulario
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
            for field, errors in form.errors.items():
                for error in errors:
                    field_name = form.fields[field].label if field in form.fields else field
                    messages.error(request, f'{field_name}: {error}')
    else:
        form = EmpresaForm()
        
    return render(request, 'etp_practica/crear_empresa.html', {'form': form})

def lista_empresas(request):
    empresas = Empresa.objects.all().order_by('nombre')
    return render(request, 'etp_practica/lista_empresas.html', {
        'lista_empresas': empresas,
        'total_empresas': empresas.count()
    })
    
def detalle_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, pk=empresa_id)
    etapas = EtapaPractica.objects.filter(empresa=empresa)
    
    stats = {
        'total': etapas.count(),
        'activos': etapas.filter(estado='PRODUCTIVA').count(),
        'finalizados': etapas.filter(estado='FINALIZADO').count(),
        'retirados': etapas.filter(estado='RETIRADO').count(),
        'lectiva': etapas.filter(estado='LECTIVA').count(),
        'aplazados': etapas.filter(estado='APLAZADO').count(),
    }
    
    return render(request, 'etp_practica/detalle_empresas.html', {
        'empresa': empresa, 
        'stats': stats,
        'etapas_recientes': etapas.order_by('-fecha_inicio')[:5]
    })

def aprendices_asignados(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    etapas = EtapaPractica.objects.filter(empresa=empresa).select_related('aprendiz')
    
    # Estadísticas
    total_aprendices = etapas.count()
    con_alertas = etapas.filter(estado__in=['APLAZADO', 'RETIRADO']).count()
    finalizados = etapas.filter(estado='FINALIZADO').count()
    activos = etapas.filter(estado='PRODUCTIVA').count()
    
    context = {
        'empresa': empresa,
        'etapas': etapas.order_by('-fecha_inicio'),
        'total_aprendices': total_aprendices,
        'con_alertas': con_alertas,
        'finalizados': finalizados,
        'activos': activos,
    }
    return render(request, 'etp_practica/aprendices_asignados.html', context)

def bitacoras(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    etapas = EtapaPractica.objects.filter(empresa=empresa).select_related('aprendiz')
    
    # Estadísticas de bitácoras
    sin_iniciar = etapas.filter(estado='LECTIVA').count()
    desertaron = etapas.filter(estado='RETIRADO').count()
    enviadas = etapas.filter(estado='PRODUCTIVA').count()
    revisadas = etapas.filter(estado='FINALIZADO').count()
    con_observaciones = etapas.filter(estado='APLAZADO').count()
    
    context = {
        'empresa': empresa,
        'etapas': etapas.order_by('-fecha_inicio'),
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
            try:
                empresa_actualizada = form.save()
                messages.success(request, f'Empresa "{empresa_actualizada.nombre}" actualizada exitosamente.')
                return redirect('etp_practica:detalle_empresa', empresa_id=empresa_actualizada.id)
            except IntegrityError as e:
                if 'nit' in str(e):
                    messages.error(request, 'Error: Ya existe una empresa con este NIT.')
                    form.add_error('nit', 'Ya existe una empresa con este NIT.')
                elif 'email' in str(e):
                    messages.error(request, 'Error: Ya existe una empresa con este email.')
                    form.add_error('email', 'Ya existe una empresa con este email.')
                else:
                    messages.error(request, 'Error al actualizar la empresa. Verifique que todos los datos sean únicos.')
            except Exception as e:
                messages.error(request, f'Error inesperado al actualizar la empresa: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
            for field, errors in form.errors.items():
                for error in errors:
                    field_name = form.fields[field].label if field in form.fields else field
                    messages.error(request, f'{field_name}: {error}')
    else:
        form = EmpresaForm(instance=empresa)
    
    return render(request, 'etp_practica/editar_empresa.html', {
        'form': form, 
        'empresa': empresa
    })

@csrf_protect
def crear_etapa_practica(request):
    if request.method == 'POST':
        form = EtapaPracticaForm(request.POST)
        if form.is_valid():
            try:
                etapa = form.save()
                messages.success(request, f'Etapa de práctica para {etapa.aprendiz.nombre} creada exitosamente.')
                return redirect('etp_practica:detalle_empresa', empresa_id=etapa.empresa.id)
            except Exception as e:
                messages.error(request, f'Error al crear la etapa de práctica: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
            for field, errors in form.errors.items():
                for error in errors:
                    field_name = form.fields[field].label if field in form.fields else field
                    messages.error(request, f'{field_name}: {error}')
    else:
        form = EtapaPracticaForm()
        
    return render(request, 'etp_practica/crear_etapa_practica.html', {'form': form})

def eliminar_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    
    if request.method == 'POST':
        try:
            # Verificar si tiene etapas de práctica asociadas
            etapas_count = EtapaPractica.objects.filter(empresa=empresa).count()
            if etapas_count > 0:
                messages.error(request, f'No se puede eliminar la empresa "{empresa.nombre}" porque tiene {etapas_count} etapa(s) de práctica asociada(s).')
                return redirect('etp_practica:detalle_empresa', empresa_id=empresa.id)
            
            nombre_empresa = empresa.nombre
            empresa.delete()
            messages.success(request, f'Empresa "{nombre_empresa}" eliminada exitosamente.')
            return redirect('etp_practica:lista_empresas')
            
        except Exception as e:
            messages.error(request, f'Error al eliminar la empresa: {str(e)}')
            return redirect('etp_practica:detalle_empresa', empresa_id=empresa.id)
    
    # Si es GET, mostrar confirmación
    etapas_count = EtapaPractica.objects.filter(empresa=empresa).count()
    return render(request, 'etp_practica/confirmar_eliminacion.html', {
        'empresa': empresa,
        'etapas_count': etapas_count
    })