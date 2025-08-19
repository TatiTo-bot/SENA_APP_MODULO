from django.db import models
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

    def __str__(self):
        return f"{self.aprendiz.nombre} - {self.empresa.nombre}"

    class Meta:
        verbose_name = "Etapa de Práctica"
        verbose_name_plural = "Etapas de Práctica"