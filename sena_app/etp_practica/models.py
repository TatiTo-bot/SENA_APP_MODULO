from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from aprendices.models import Aprendiz

class Empresa(models.Model):
    nombre = models.CharField(max_length=100)
    nit = models.CharField(max_length=50, unique=True)
    direccion = models.CharField(max_length=300)
    ciudad = models.CharField(max_length=50)
    telefono = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

class AsignacionAprendiz(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de asignación'),
        ('ASIGNADO', 'Asignado a empresa'),
        ('CONFIRMADO', 'Confirmado por empresa'),
        ('RECHAZADO', 'Rechazado por empresa'),
        ('INICIADO', 'Etapa práctica iniciada'),
        ('CANCELADO', 'Asignación cancelada'),
    ]
    
    MODALIDAD_CHOICES = [
        ('PRESENCIAL', 'Presencial'),
        ('REMOTO', 'Trabajo remoto'),
        ('HIBRIDO', 'Modalidad híbrida'),
    ]
    
    # Relaciones principales
    aprendiz = models.ForeignKey(
        Aprendiz, 
        on_delete=models.CASCADE,
        related_name='asignaciones'
    )
    empresa = models.ForeignKey(
        Empresa, 
        on_delete=models.CASCADE,
        related_name='asignaciones_aprendices'
    )
    
    # Información de la asignación
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)
    fecha_inicio_propuesta = models.DateField(
        help_text="Fecha propuesta para iniciar la etapa práctica"
    )
    fecha_fin_propuesta = models.DateField(
        help_text="Fecha propuesta para finalizar la etapa práctica"
    )
    
    # Estado y modalidad
    estado = models.CharField(
        max_length=15, 
        choices=ESTADO_CHOICES, 
        default='PENDIENTE'
    )
    modalidad = models.CharField(
        max_length=15,
        choices=MODALIDAD_CHOICES,
        default='PRESENCIAL'
    )
    
    # Información adicional
    tutor_propuesto = models.CharField(
        max_length=200,
        help_text="Nombre del tutor que supervisará al aprendiz"
    )
    area_trabajo = models.CharField(
        max_length=100,
        blank=True,
        help_text="Área o departamento donde trabajará"
    )
    objetivos_propuestos = models.TextField(
        blank=True,
        help_text="Objetivos específicos para la etapa práctica"
    )
    observaciones = models.TextField(
        blank=True,
        help_text="Observaciones adicionales sobre la asignación"
    )
    
    # Información de contacto
    contacto_empresa = models.CharField(
        max_length=200,
        blank=True,
        help_text="Persona de contacto en la empresa"
    )
    telefono_contacto = models.CharField(
        max_length=15,
        blank=True
    )
    email_contacto = models.EmailField(
        blank=True,
        help_text="Email de contacto en la empresa"
    )
    
    # Campos de auditoría
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.CharField(
        max_length=100,
        blank=True,
        help_text="Usuario que creó la asignación"
    )
    
    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        # Validar que la fecha de fin sea posterior a la de inicio
        if self.fecha_inicio_propuesta and self.fecha_fin_propuesta:
            if self.fecha_fin_propuesta <= self.fecha_inicio_propuesta:
                raise ValidationError({
                    'fecha_fin_propuesta': 'La fecha de fin debe ser posterior a la fecha de inicio.'
                })
        
        # Validar que no exista una asignación activa para el mismo aprendiz
        if self.pk is None:  # Solo para nuevas asignaciones
            asignacion_activa = AsignacionAprendiz.objects.filter(
                aprendiz=self.aprendiz,
                estado__in=['PENDIENTE', 'ASIGNADO', 'CONFIRMADO', 'INICIADO']
            ).exists()
            
            if asignacion_activa:
                raise ValidationError({
                    'aprendiz': 'Este aprendiz ya tiene una asignación activa.'
                })
    
    def confirmar_asignacion(self):
        """Método para confirmar la asignación por parte de la empresa"""
        if self.estado == 'ASIGNADO':
            self.estado = 'CONFIRMADO'
            self.fecha_confirmacion = timezone.now()
            self.save()
            return True
        return False
    
    def iniciar_etapa_practica(self):
        """Método para marcar que se ha iniciado la etapa práctica"""
        if self.estado == 'CONFIRMADO':
            self.estado = 'INICIADO'
            self.save()
            
            # Crear automáticamente el registro de EtapaPractica
            etapa_practica = EtapaPractica.objects.create(
                aprendiz=self.aprendiz,
                empresa=self.empresa,
                tutor=self.tutor_propuesto,
                fecha_inicio=self.fecha_inicio_propuesta,
                fecha_fin=self.fecha_fin_propuesta,
                objetivos=self.objetivos_propuestos,
                estado='PRODUCTIVA'
            )
            return etapa_practica
        return None
    
    def rechazar_asignacion(self, motivo=""):
        """Método para rechazar la asignación"""
        if self.estado in ['PENDIENTE', 'ASIGNADO']:
            self.estado = 'RECHAZADO'
            if motivo:
                self.observaciones += f"\nMotivo de rechazo: {motivo}"
            self.save()
            return True
        return False
    
    def get_duracion_propuesta(self):
        """Calcula la duración propuesta en días"""
        if self.fecha_inicio_propuesta and self.fecha_fin_propuesta:
            return (self.fecha_fin_propuesta - self.fecha_inicio_propuesta).days
        return 0
    
    def __str__(self):
        return f"{self.aprendiz.nombre} → {self.empresa.nombre} ({self.get_estado_display()})"
    
    class Meta:
        verbose_name = "Asignación de Aprendiz"
        verbose_name_plural = "Asignaciones de Aprendices"
        ordering = ['-fecha_asignacion']
        
        # Índices para mejorar rendimiento
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_asignacion']),
            models.Index(fields=['aprendiz', 'estado']),
            models.Index(fields=['empresa', 'estado']),
        ]

class EtapaPractica(models.Model):
    ESTADOS_CHOICES = [
        ('LECTIVA', 'En etapa lectiva'),
        ('PRODUCTIVA', 'En etapa productiva'), 
        ('FINALIZADO', 'Formación finalizada'),
        ('RETIRADO', 'Retirado'),
        ('APLAZADO', 'Aplazado'),
    ]

    aprendiz = models.ForeignKey(Aprendiz, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    tutor = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    objetivos = models.TextField(blank=True)
    bitacora = models.TextField(blank=True)
    estado = models.CharField(max_length=15, choices=ESTADOS_CHOICES, default='LECTIVA')
    
    # Campo opcional para vincular con la asignación original
    asignacion_origen = models.OneToOneField(
        AsignacionAprendiz,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='etapa_practica_creada'
    )

    def __str__(self):
        return f"{self.aprendiz.nombre} - {self.empresa.nombre}"

    class Meta:
        verbose_name = "Etapa de Práctica"
        verbose_name_plural = "Etapas de Práctica"