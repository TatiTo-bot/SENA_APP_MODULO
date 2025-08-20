from django import forms
from .models import Empresa, EtapaPractica

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nombre', 'nit', 'direccion', 'ciudad', 'telefono', 'email']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: TechCorp Solutions S.A.S',
                'required': True
            }),
            'nit': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: 900.123.456-7',
                'required': True
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: Carrera 15 #93-47, Zona Rosa',
                'required': True
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: Bogotá D.C.',
                'required': True
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: +57 1 234-5678',
                'required': True,
                'type': 'tel'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: contacto@empresa.com',
                'required': True
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer todos los campos requeridos
        for field_name, field in self.fields.items():
            field.required = True
            # Agregar clases CSS adicionales si es necesario
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'

    def clean_nit(self):
        nit = self.cleaned_data.get('nit')
        if nit:
            # Limpiar el NIT de puntos y guiones para validación
            nit_limpio = ''.join(filter(str.isdigit, nit))
            if len(nit_limpio) < 8:
                raise forms.ValidationError('El NIT debe tener al menos 8 dígitos.')
        return nit

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Verificar si ya existe una empresa con este email
            if self.instance.pk:
                # Si estamos editando, excluir la instancia actual
                if Empresa.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError('Ya existe una empresa con este correo electrónico.')
            else:
                # Si es una nueva empresa
                if Empresa.objects.filter(email=email).exists():
                    raise forms.ValidationError('Ya existe una empresa con este correo electrónico.')
        return email

class EtapaPracticaForm(forms.ModelForm):
    class Meta:
        model = EtapaPractica
        fields = ['aprendiz', 'empresa', 'tutor', 'fecha_inicio', 'fecha_fin', 'objetivos', 'bitacora', 'estado']
        widgets = {
            'aprendiz': forms.Select(attrs={'class': 'form-control'}),
            'empresa': forms.Select(attrs={'class': 'form-control'}),
            'tutor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del tutor'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'objetivos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'bitacora': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar etiquetas y hacer campos requeridos
        self.fields['aprendiz'].label = 'Aprendiz'
        self.fields['empresa'].label = 'Empresa'
        self.fields['tutor'].label = 'Tutor Empresarial'
        self.fields['fecha_inicio'].label = 'Fecha de Inicio'
        self.fields['fecha_fin'].label = 'Fecha de Finalización'
        self.fields['objetivos'].label = 'Objetivos de la Práctica'
        self.fields['bitacora'].label = 'Bitácora'
        self.fields['estado'].label = 'Estado'
        
        # Hacer campos requeridos
        required_fields = ['aprendiz', 'empresa', 'tutor', 'fecha_inicio', 'estado']
        for field_name in required_fields:
            self.fields[field_name].required = True

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        if fecha_inicio and fecha_fin:
            if fecha_fin <= fecha_inicio:
                raise forms.ValidationError('La fecha de finalización debe ser posterior a la fecha de inicio.')

        return cleaned_data