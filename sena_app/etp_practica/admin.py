from django.contrib import admin
from .models import Empresa, EtapaPractica, AsignacionAprendiz

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'nit', 'ciudad', 'telefono', 'email']
    list_filter = ['ciudad']
    search_fields = ['nombre', 'nit', 'email']
    ordering = ['nombre']

@admin.register(AsignacionAprendiz)
class AsignacionAprendizAdmin(admin.ModelAdmin):
    list_display = [
        'aprendiz', 
        'empresa', 
        'estado', 
        'modalidad', 
        'fecha_asignacion',
        'fecha_inicio_propuesta',
        'tutor_propuesto'
    ]
    list_filter = [
        'estado', 
        'modalidad', 
        'fecha_asignacion', 
        'empresa__ciudad'
    ]
    search_fields = [
        'aprendiz__nombre',
        'aprendiz__documento', 
        'empresa__nombre',
        'tutor_propuesto'
    ]
    date_hierarchy = 'fecha_asignacion'
    ordering = ['-fecha_asignacion']
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('aprendiz', 'empresa', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio_propuesta', 'fecha_fin_propuesta', 'fecha_confirmacion')
        }),
        ('Detalles de la Práctica', {
            'fields': ('modalidad', 'tutor_propuesto', 'area_trabajo', 'objetivos_propuestos')
        }),
        ('Información de Contacto', {
            'fields': ('contacto_empresa', 'telefono_contacto', 'email_contacto')
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('creado_por', 'fecha_actualizacion'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['fecha_asignacion', 'fecha_actualizacion', 'fecha_confirmacion']
    
    actions = ['confirmar_asignaciones', 'rechazar_asignaciones']
    
    def confirmar_asignaciones(self, request, queryset):
        """Acción para confirmar múltiples asignaciones"""
        updated = 0
        for asignacion in queryset.filter(estado='ASIGNADO'):
            if asignacion.confirmar_asignacion():
                updated += 1
        
        self.message_user(
            request, 
            f'{updated} asignación(es) confirmada(s) exitosamente.'
        )
    confirmar_asignaciones.short_description = "Confirmar asignaciones seleccionadas"
    
    def rechazar_asignaciones(self, request, queryset):
        """Acción para rechazar múltiples asignaciones"""
        updated = 0
        for asignacion in queryset.filter(estado__in=['PENDIENTE', 'ASIGNADO']):
            if asignacion.rechazar_asignacion("Rechazado desde admin"):
                updated += 1
        
        self.message_user(
            request, 
            f'{updated} asignación(es) rechazada(s) exitosamente.'
        )
    rechazar_asignaciones.short_description = "Rechazar asignaciones seleccionadas"

@admin.register(EtapaPractica)
class EtapaPracticaAdmin(admin.ModelAdmin):
    list_display = [
        'aprendiz', 
        'empresa', 
        'estado', 
        'fecha_inicio', 
        'fecha_fin',
        'tutor'
    ]
    list_filter = [
        'estado', 
        'fecha_inicio', 
        'empresa__ciudad'
    ]
    search_fields = [
        'aprendiz__nombre',
        'aprendiz__documento',
        'empresa__nombre',
        'tutor'
    ]
    date_hierarchy = 'fecha_inicio'
    ordering = ['-fecha_inicio']
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('aprendiz', 'empresa', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Detalles', {
            'fields': ('tutor', 'objetivos', 'bitacora')
        }),
        ('Vinculación', {
            'fields': ('asignacion_origen',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['asignacion_origen']