from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.db import IntegrityError
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Empresa, EtapaPractica, AsignacionAprendiz
from aprendices.models import Aprendiz
from .forms import (
    EmpresaForm, 
    AsignacionAprendizForm, 
    FiltroAsignacionesForm,
    ConfirmarAsignacionForm
)
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
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
            for field, errors in form.errors.items():
                for error in errors:
                    field_name = form.fields[field].label if field in form.fields else field
                    messages.error(request, f'{field_name}: {error}')
    else:
        form = EmpresaForm()
        
    return render(request, 'etp_practica/crear_empresa.html', {'form': form})

def lista_empresas(request):
    empresas = Empresa.objects.annotate(
        total_asignaciones=Count('asignaciones_aprendices'),
        asignaciones_activas=Count('asignaciones_aprendices', 
                                    filter=Q(asignaciones_aprendices__estado__in=['CONFIRMADO', 'INICIADO']))
    ).order_by('nombre')
    
    return render(request, 'etp_practica/lista_empresas.html', {
        'lista_empresas': empresas,
        'total_empresas': empresas.count()
    })
    
def detalle_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, pk=empresa_id)
    etapas = EtapaPractica.objects.filter(empresa=empresa)
    asignaciones = AsignacionAprendiz.objects.filter(empresa=empresa)
    
    # Estadísticas de etapas prácticas
    stats_etapas = {
        'total': etapas.count(),
        'activos': etapas.filter(estado='PRODUCTIVA').count(),
        'finalizados': etapas.filter(estado='FINALIZADO').count(),
        'retirados': etapas.filter(estado='RETIRADO').count(),
        'lectiva': etapas.filter(estado='LECTIVA').count(),
        'aplazados': etapas.filter(estado='APLAZADO').count(),
    }
    
    # Estadísticas de asignaciones
    stats_asignaciones = {
        'total': asignaciones.count(),
        'pendientes': asignaciones.filter(estado='PENDIENTE').count(),
        'asignados': asignaciones.filter(estado='ASIGNADO').count(),
        'confirmados': asignaciones.filter(estado='CONFIRMADO').count(),
        'rechazados': asignaciones.filter(estado='RECHAZADO').count(),
        'iniciados': asignaciones.filter(estado='INICIADO').count(),
    }
    
    return render(request, 'etp_practica/detalle_empresas.html', {
        'empresa': empresa, 
        'stats_etapas': stats_etapas,
        'stats_asignaciones': stats_asignaciones,
        'etapas_recientes': etapas.order_by('-fecha_inicio')[:5],
        'asignaciones_recientes': asignaciones.order_by('-fecha_asignacion')[:5]
    })

def aprendices_asignados(request, empresa_id):
    empresa = get_object_or_404(Empresa, pk=empresa_id)
    
    # Obtener asignaciones y etapas prácticas
    asignaciones = AsignacionAprendiz.objects.filter(empresa=empresa).select_related('aprendiz')
    etapas_practica = EtapaPractica.objects.filter(empresa=empresa).select_related('aprendiz')
    
    # Estadísticas de asignaciones
    stats_asignaciones = {
        'total': asignaciones.count(),
        'pendientes': asignaciones.filter(estado='PENDIENTE').count(),
        'confirmados': asignaciones.filter(estado='CONFIRMADO').count(),
        'rechazados': asignaciones.filter(estado='RECHAZADO').count(),
        'iniciados': asignaciones.filter(estado='INICIADO').count(),
    }
    
    # Estadísticas de etapas prácticas
    stats_etapas = {
        'productivos': etapas_practica.filter(estado='PRODUCTIVA').count(),
        'finalizados': etapas_practica.filter(estado='FINALIZADO').count(),
        'lectivos': etapas_practica.filter(estado='LECTIVA').count(),
        'retirados': etapas_practica.filter(estado='RETIRADO').count(),
    }
    
    context = {
        'empresa': empresa,
        'asignaciones': asignaciones.order_by('-fecha_asignacion'),
        'etapas_practica': etapas_practica.order_by('-fecha_inicio'),
        'stats_asignaciones': stats_asignaciones,
        'stats_etapas': stats_etapas,
    }
    return render(request, 'etp_practica/aprendices_asignados.html', context)

@csrf_protect
def asignar_aprendiz(request, empresa_id):
    empresa = get_object_or_404(Empresa, pk=empresa_id)
    
    if request.method == 'POST':
        form = AsignacionAprendizForm(request.POST, empresa_id=empresa_id)
        if form.is_valid():
            try:
                asignacion = form.save(commit=False)
                asignacion.empresa = empresa
                asignacion.estado = 'ASIGNADO'
                if request.user.is_authenticated:
                    asignacion.creado_por = request.user.username
                asignacion.save()
                
                messages.success(
                    request, 
                    f'¡Aprendiz "{asignacion.aprendiz.nombre}" asignado exitosamente a la empresa!'
                )
                return redirect('etp_practica:aprendices_asignados', empresa_id=empresa.id)
                
            except Exception as e:
                messages.error(request, f'Error al crear la asignación: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = AsignacionAprendizForm(empresa_id=empresa_id)
    
    # Contar aprendices disponibles
    aprendices_ocupados = AsignacionAprendiz.objects.filter(
        estado__in=['PENDIENTE', 'ASIGNADO', 'CONFIRMADO', 'INICIADO']
    ).values_list('aprendiz_id', flat=True)
    
    aprendices_disponibles = Aprendiz.objects.exclude(
        id__in=aprendices_ocupados
    ).count()
    
    context = {
        'empresa': empresa,
        'form': form,
        'aprendices_disponibles': aprendices_disponibles
    }
    return render(request, 'etp_practica/asignar_aprendiz.html', context)

def gestionar_asignaciones(request, empresa_id=None):
    """Vista para gestionar todas las asignaciones (con filtros opcionales por empresa)"""
    # Base queryset
    asignaciones = AsignacionAprendiz.objects.select_related('aprendiz', 'empresa')
    
    # Si se especifica empresa, filtrar por ella
    empresa = None
    if empresa_id:
        empresa = get_object_or_404(Empresa, pk=empresa_id)
        asignaciones = asignaciones.filter(empresa=empresa)
    
    # Procesar filtros
    form_filtros = FiltroAsignacionesForm(request.GET)
    if form_filtros.is_valid():
        # Filtro por búsqueda de texto
        if form_filtros.cleaned_data.get('buscar'):
            buscar = form_filtros.cleaned_data['buscar']
            asignaciones = asignaciones.filter(
                Q(aprendiz__nombre__icontains=buscar) |
                Q(aprendiz__documento__icontains=buscar) |
                Q(empresa__nombre__icontains=buscar) |
                Q(tutor_propuesto__icontains=buscar)
            )
        
        # Filtro por estado
        if form_filtros.cleaned_data.get('estado'):
            asignaciones = asignaciones.filter(estado=form_filtros.cleaned_data['estado'])
        
        # Filtro por modalidad
        if form_filtros.cleaned_data.get('modalidad'):
            asignaciones = asignaciones.filter(modalidad=form_filtros.cleaned_data['modalidad'])
        
        # Filtro por empresa (solo si no se especificó empresa_id)
        if not empresa_id and form_filtros.cleaned_data.get('empresa'):
            asignaciones = asignaciones.filter(empresa=form_filtros.cleaned_data['empresa'])
        
        # Filtros por fecha
        if form_filtros.cleaned_data.get('fecha_desde'):
            asignaciones = asignaciones.filter(fecha_asignacion__gte=form_filtros.cleaned_data['fecha_desde'])
        
        if form_filtros.cleaned_data.get('fecha_hasta'):
            asignaciones = asignaciones.filter(fecha_asignacion__lte=form_filtros.cleaned_data['fecha_hasta'])
    
    # Paginación
    paginator = Paginator(asignaciones.order_by('-fecha_asignacion'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    stats = {
        'total': asignaciones.count(),
        'pendientes': asignaciones.filter(estado='PENDIENTE').count(),
        'asignados': asignaciones.filter(estado='ASIGNADO').count(),
        'confirmados': asignaciones.filter(estado='CONFIRMADO').count(),
        'rechazados': asignaciones.filter(estado='RECHAZADO').count(),
        'iniciados': asignaciones.filter(estado='INICIADO').count(),
        'cancelados': asignaciones.filter(estado='CANCELADO').count(),
    }
    
    context = {
        'asignaciones': page_obj,
        'form_filtros': form_filtros,
        'stats': stats,
        'empresa': empresa,
        'total_resultados': asignaciones.count()
    }
    
    return render(request, 'etp_practica/gestionar_asignaciones.html', context)

@csrf_protect
def confirmar_asignacion(request, asignacion_id):
    """Vista para que la empresa confirme o rechace una asignación"""
    asignacion = get_object_or_404(AsignacionAprendiz, pk=asignacion_id)
    
    # Solo asignaciones en estado ASIGNADO pueden ser confirmadas/rechazadas
    if asignacion.estado != 'ASIGNADO':
        messages.error(request, 'Esta asignación no puede ser modificada.')
        return redirect('etp_practica:detalle_asignacion', asignacion_id=asignacion.id)
    
    if request.method == 'POST':
        form = ConfirmarAsignacionForm(request.POST)
        if form.is_valid():
            accion = form.cleaned_data['accion']
            observaciones = form.cleaned_data.get('observaciones', '')
            
            if accion == 'confirmar':
                if asignacion.confirmar_asignacion():
                    if observaciones:
                        asignacion.observaciones += f"\nConfirmado: {observaciones}"
                        asignacion.save()
                    messages.success(request, 'Asignación confirmada exitosamente.')
                else:
                    messages.error(request, 'No se pudo confirmar la asignación.')
            
            elif accion == 'rechazar':
                if asignacion.rechazar_asignacion(observaciones):
                    messages.success(request, 'Asignación rechazada.')
                else:
                    messages.error(request, 'No se pudo rechazar la asignación.')
            
            return redirect('etp_practica:detalle_asignacion', asignacion_id=asignacion.id)
    else:
        form = ConfirmarAsignacionForm()
    
    context = {
        'asignacion': asignacion,
        'form': form
    }
    return render(request, 'etp_practica/confirmar_asignacion.html', context)

def detalle_asignacion(request, asignacion_id):
    """Vista para ver el detalle completo de una asignación"""
    asignacion = get_object_or_404(
        AsignacionAprendiz.objects.select_related('aprendiz', 'empresa'),
        pk=asignacion_id
    )
    
    # Verificar si ya existe etapa práctica creada
    etapa_practica = None
    if hasattr(asignacion, 'etapa_practica_creada'):
        etapa_practica = asignacion.etapa_practica_creada
    
    context = {
        'asignacion': asignacion,
        'etapa_practica': etapa_practica,
        'puede_confirmar': asignacion.estado == 'ASIGNADO',
        'puede_iniciar': asignacion.estado == 'CONFIRMADO',
    }
    return render(request, 'etp_practica/detalle_asignacion.html', context)

@csrf_protect
def iniciar_etapa_practica(request, asignacion_id):
    """Vista para iniciar la etapa práctica desde una asignación confirmada"""
    asignacion = get_object_or_404(AsignacionAprendiz, pk=asignacion_id)
    
    if asignacion.estado != 'CONFIRMADO':
        messages.error(request, 'Solo se pueden iniciar asignaciones confirmadas.')
        return redirect('etp_practica:detalle_asignacion', asignacion_id=asignacion.id)
    
    if request.method == 'POST':
        try:
            etapa_practica = asignacion.iniciar_etapa_practica()
            if etapa_practica:
                messages.success(
                    request, 
                    f'¡Etapa práctica iniciada exitosamente para {asignacion.aprendiz.nombre}!'
                )
                return redirect('etp_practica:bitacoras', empresa_id=asignacion.empresa.id)
            else:
                messages.error(request, 'No se pudo iniciar la etapa práctica.')
        except Exception as e:
            messages.error(request, f'Error al iniciar etapa práctica: {str(e)}')
    
    return redirect('etp_practica:detalle_asignacion', asignacion_id=asignacion.id)

@csrf_protect
def editar_asignacion(request, asignacion_id):
    """Vista para editar una asignación (solo si está en estado PENDIENTE o ASIGNADO)"""
    asignacion = get_object_or_404(AsignacionAprendiz, pk=asignacion_id)
    
    if asignacion.estado not in ['PENDIENTE', 'ASIGNADO']:
        messages.error(request, 'Esta asignación no puede ser editada.')
        return redirect('etp_practica:detalle_asignacion', asignacion_id=asignacion.id)
    
    if request.method == 'POST':
        form = AsignacionAprendizForm(request.POST, instance=asignacion)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Asignación actualizada exitosamente.')
                return redirect('etp_practica:detalle_asignacion', asignacion_id=asignacion.id)
            except Exception as e:
                messages.error(request, f'Error al actualizar la asignación: {str(e)}')
    else:
        form = AsignacionAprendizForm(instance=asignacion)
    
    context = {
        'asignacion': asignacion,
        'form': form
    }
    return render(request, 'etp_practica/editar_asignacion.html', context)

@csrf_protect
def cancelar_asignacion(request, asignacion_id):
    """Vista para cancelar una asignación"""
    asignacion = get_object_or_404(AsignacionAprendiz, pk=asignacion_id)
    
    if asignacion.estado in ['INICIADO', 'CANCELADO']:
        messages.error(request, 'Esta asignación no puede ser cancelada.')
        return redirect('etp_practica:detalle_asignacion', asignacion_id=asignacion.id)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo', '')
        asignacion.estado = 'CANCELADO'
        if motivo:
            asignacion.observaciones += f"\nCancelado: {motivo}"
        asignacion.save()
        
        messages.success(request, 'Asignación cancelada exitosamente.')
        return redirect('etp_practica:aprendices_asignados', empresa_id=asignacion.empresa.id)
    
    context = {
        'asignacion': asignacion
    }
    return render(request, 'etp_practica/cancelar_asignacion.html', context)

def bitacoras(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    etapas = EtapaPractica.objects.filter(empresa=empresa).select_related('aprendiz')
    
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

def eliminar_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    
    if request.method == 'POST':
        try:
            etapas_count = EtapaPractica.objects.filter(empresa=empresa).count()
            asignaciones_count = AsignacionAprendiz.objects.filter(empresa=empresa).count()
            
            if etapas_count > 0 or asignaciones_count > 0:
                messages.error(
                    request, 
                    f'No se puede eliminar la empresa "{empresa.nombre}" porque tiene '
                    f'{etapas_count} etapa(s) de práctica y {asignaciones_count} asignación(es) asociada(s).'
                )
                return redirect('etp_practica:detalle_empresa', empresa_id=empresa.id)
            
            nombre_empresa = empresa.nombre
            empresa.delete()
            messages.success(request, f'Empresa "{nombre_empresa}" eliminada exitosamente.')
            return redirect('etp_practica:lista_empresas')
            
        except Exception as e:
            messages.error(request, f'Error al eliminar la empresa: {str(e)}')
            return redirect('etp_practica:detalle_empresa', empresa_id=empresa.id)
    
    etapas_count = EtapaPractica.objects.filter(empresa=empresa).count()
    asignaciones_count = AsignacionAprendiz.objects.filter(empresa=empresa).count()
    
    return render(request, 'etp_practica/confirmar_eliminacion.html', {
        'empresa': empresa,
        'etapas_count': etapas_count,
        'asignaciones_count': asignaciones_count
    })

def api_aprendices_disponibles(request):
    """API endpoint para obtener aprendices disponibles"""
    aprendices_ocupados = AsignacionAprendiz.objects.filter(
        estado__in=['PENDIENTE', 'ASIGNADO', 'CONFIRMADO', 'INICIADO']
    ).values_list('aprendiz_id', flat=True)
    
    aprendices = Aprendiz.objects.exclude(
        id__in=aprendices_ocupados
    ).values('id', 'nombre', 'documento')
    
    return JsonResponse({
        'aprendices': list(aprendices),
        'total': aprendices.count()
    })

def api_estadisticas_empresa(request, empresa_id):
    """API endpoint para obtener estadísticas actualizadas de una empresa"""
    empresa = get_object_or_404(Empresa, pk=empresa_id)
    
    asignaciones = AsignacionAprendiz.objects.filter(empresa=empresa)
    etapas = EtapaPractica.objects.filter(empresa=empresa)
    
    datos = {
        'asignaciones': {
            'total': asignaciones.count(),
            'pendientes': asignaciones.filter(estado='PENDIENTE').count(),
            'confirmados': asignaciones.filter(estado='CONFIRMADO').count(),
            'rechazados': asignaciones.filter(estado='RECHAZADO').count(),
            'iniciados': asignaciones.filter(estado='INICIADO').count(),
        },
        'etapas': {
            'total': etapas.count(),
            'productivos': etapas.filter(estado='PRODUCTIVA').count(),
            'finalizados': etapas.filter(estado='FINALIZADO').count(),
            'retirados': etapas.filter(estado='RETIRADO').count(),
        }
    }
    
    return JsonResponse(datos)