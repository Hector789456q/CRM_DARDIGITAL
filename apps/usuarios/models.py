

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    """Usuario personalizado del sistema"""
    
    ROLES = [
        ('ASESOR', 'Asesor'),
        ('BACK_OFFICE', 'Back Office'),
        ('SUPERVISOR', 'Supervisor'),
        ('ENCARGADO_SEGUIMIENTO_M', 'Encargado Seguimiento (Hombre)'),
        ('ENCARGADO_SEGUIMIENTO_F', 'Encargada Seguimiento (Mujer)'),
        ('DUEÑO', 'Dueño'),
    ]
    
    MODALIDADES = [
        ('CALL_CENTER', 'Call Center'),
        ('CAMPO', 'Campo'),
        ('AMBAS', 'Ambas'),
    ]
    
    TURNOS = [
        ('MAÑANA', 'Mañana'),
        ('TARDE', 'Tarde'),
        ('AMBOS', 'Ambos'),
    ]
    
    rol = models.CharField(max_length=30, choices=ROLES, default='ASESOR')
    modalidad = models.CharField(max_length=20, choices=MODALIDADES, null=True, blank=True)
    turno = models.CharField(max_length=10, choices=TURNOS, null=True, blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"
    
    def es_asesor(self):
        return self.rol == 'ASESOR'
    
    def es_back_office(self):
        return self.rol == 'BACK_OFFICE'
    
    def es_supervisor(self):
        return self.rol == 'SUPERVISOR'
    
    def es_dueño(self):
        return self.rol == 'DUEÑO'