from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from aprendices.models import Aprendiz
from .models import Empresa, AsignacionAprendiz, EtapaPractica

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nombre', 'nit', 'direccion', 'ciudad', 'telefono', 'email']
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la empresa'
            }),
            'nit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'NIT de la empresa'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa'
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@empresa.com'
            }),
        }

class EtapaPracticaForm(forms.ModelForm):
    class Meta:
        model = EtapaPractica
        fields = ['aprendiz', 'empresa', 'tutor', 'fecha_inicio', 'fecha_fin', 'objetivos', 'estado']
        
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'objetivos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tutor': forms.TextInput(attrs={'class': 'form-control'}),
        }

class AsignacionAprendizForm(forms.ModelForm):
    """
    Formulario para crear y editar asignaciones de aprendices a empresas
    """
    
    class Meta:
        model = AsignacionAprendiz
        fields = [
            'aprendiz',
            'empresa', 
            'fecha_inicio_propuesta',
            'fecha_fin_propuesta',
            'modalidad',
            'tutor_propuesto',
            'area_trabajo',
            'objetivos_propuestos',
            'contacto_empresa',
            'telefono_contacto',
            'email_contacto',
            'observaciones'
        ]
        
        widgets = {
            'aprendiz': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'empresa': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'fecha_inicio_propuesta': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True
            }),
            'fecha_fin_propuesta': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control',
                'required': True
            }),
            'modalidad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tutor_propuesto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del tutor empresarial',
                'required': True
            }),
            'area_trabajo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Desarrollo, Marketing, Diseño, etc.'
            }),
            'objetivos_propuestos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe los objetivos específicos que el aprendiz debe cumplir...'
            }),
            'contacto_empresa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la persona de contacto'
            }),
            'telefono_contacto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de contacto'
            }),
            'email_contacto': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@empresa.com'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            })
        }
        
        labels = {
            'aprendiz': 'Aprendiz',
            'empresa': 'Empresa',
            'fecha_inicio_propuesta': 'Fecha de inicio propuesta',
            'fecha_fin_propuesta': 'Fecha de finalización propuesta',
            'modalidad': 'Modalidad de trabajo',
            'tutor_propuesto': 'Tutor empresarial',
            'area_trabajo': 'Área de trabajo',
            'objetivos_propuestos': 'Objetivos de la práctica',
            'contacto_empresa': 'Persona de contacto',
            'telefono_contacto': 'Teléfono de contacto',
            'email_contacto': 'Email de contacto',
            'observaciones': 'Observaciones'
        }
    
    def __init__(self, *args, **kwargs):
        empresa_id = kwargs.pop('empresa_id', None)
        super().__init__(*args, **kwargs)
        
        # Si se proporciona empresa_id, preseleccionar la empresa
        if empresa_id:
            self.fields['empresa'].initial = empresa_id
            self.fields['empresa'].widget.attrs['disabled'] = True
        
        # Filtrar solo aprendices disponibles (sin asignación activa)
        aprendices_ocupados = AsignacionAprendiz.objects.filter(
            estado__in=['PENDIENTE', 'ASIGNADO', 'CONFIRMADO', 'INICIADO']
        ).values_list('aprendiz_id', flat=True)
        
        self.fields['aprendiz'].queryset = Aprendiz.objects.exclude(
            id__in=aprendices_ocupados
        ).order_by('nombre')
        
        # Establecer fechas por defecto
        today = date.today()
        self.fields['fecha_inicio_propuesta'].initial = today + timedelta(days=30)
        self.fields['fecha_fin_propuesta'].initial = today + timedelta(days=210)  # ~6 meses
    
    def clean_fecha_inicio_propuesta(self):
        fecha_inicio = self.cleaned_data.get('fecha_inicio_propuesta')
        if fecha_inicio:
            # La fecha de inicio no puede ser en el pasado
            if fecha_inicio < date.today():
                raise ValidationError("La fecha de inicio no puede ser en el pasado.")
            
            # La fecha de inicio no puede ser muy lejana (más de 1 año)
            if fecha_inicio > date.today() + timedelta(days=365):
                raise ValidationError("La fecha de inicio no puede ser más de un año en el futuro.")
        
        return fecha_inicio
    
    def clean_fecha_fin_propuesta(self):
        fecha_fin = self.cleaned_data.get('fecha_fin_propuesta')
        if fecha_fin:
            # Similar validación para fecha fin
            if fecha_fin < date.today():
                raise ValidationError("La fecha de finalización no puede ser en el pasado.")
        
        return fecha_fin
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio_propuesta')
        fecha_fin = cleaned_data.get('fecha_fin_propuesta')
        aprendiz = cleaned_data.get('aprendiz')
        
        # Validar fechas
        if fecha_inicio and fecha_fin:
            if fecha_fin <= fecha_inicio:
                raise ValidationError({
                    'fecha_fin_propuesta': 'La fecha de finalización debe ser posterior a la fecha de inicio.'
                })
            
            # Validar duración mínima (al menos 3 meses)
            duracion = (fecha_fin - fecha_inicio).days
            if duracion < 90:
                raise ValidationError({
                    'fecha_fin_propuesta': 'La duración mínima de la práctica debe ser de 3 meses (90 días).'
                })
            
            # Validar duración máxima (no más de 12 meses)
            if duracion > 365:
                raise ValidationError({
                    'fecha_fin_propuesta': 'La duración máxima de la práctica no puede exceder 12 meses.'
                })
        
        # Validar que el aprendiz no tenga asignación activa
        if aprendiz:
            asignacion_activa = AsignacionAprendiz.objects.filter(
                aprendiz=aprendiz,
                estado__in=['PENDIENTE', 'ASIGNADO', 'CONFIRMADO', 'INICIADO']
            )
            
            # Excluir la instancia actual si estamos editando
            if self.instance.pk:
                asignacion_activa = asignacion_activa.exclude(pk=self.instance.pk)
            
            if asignacion_activa.exists():
                raise ValidationError({
                    'aprendiz': 'Este aprendiz ya tiene una asignación activa.'
                })
        
        return cleaned_data

class FiltroAsignacionesForm(forms.Form):
    """
    Formulario para filtrar asignaciones de aprendices
    """
    ESTADO_FILTRO_CHOICES = [
        ('', 'Todos los estados'),
        ('PENDIENTE', 'Pendientes'),
        ('ASIGNADO', 'Asignados'),
        ('CONFIRMADO', 'Confirmados'),
        ('RECHAZADO', 'Rechazados'),
        ('INICIADO', 'Iniciados'),
        ('CANCELADO', 'Cancelados'),
    ]
    
    MODALIDAD_FILTRO_CHOICES = [
        ('', 'Todas las modalidades'),
        ('PRESENCIAL', 'Presencial'),
        ('REMOTO', 'Remoto'),
        ('HIBRIDO', 'Híbrido'),
    ]
    
    buscar = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre de aprendiz o empresa...'
        })
    )
    
    estado = forms.ChoiceField(
        choices=ESTADO_FILTRO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    modalidad = forms.ChoiceField(
        choices=MODALIDAD_FILTRO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    empresa = forms.ModelChoiceField(
        queryset=Empresa.objects.all().order_by('nombre'),
        required=False,
        empty_label="Todas las empresas",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )

class ConfirmarAsignacionForm(forms.Form):
    """
    Formulario para que la empresa confirme o rechace una asignación
    """
    ACCION_CHOICES = [
        ('confirmar', 'Confirmar asignación'),
        ('rechazar', 'Rechazar asignación'),
    ]
    
    accion = forms.ChoiceField(
        choices=ACCION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Observaciones adicionales (opcional para confirmación, requerido para rechazo)...'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        accion = cleaned_data.get('accion')
        observaciones = cleaned_data.get('observaciones')
        
        # Si se rechaza, las observaciones son obligatorias
        if accion == 'rechazar' and not observaciones:
            raise ValidationError({
                'observaciones': 'Las observaciones son requeridas cuando se rechaza una asignación.'
            })
        
        return cleaned_data