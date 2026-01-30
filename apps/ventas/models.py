from django.db import models
from django.conf import settings
from django.utils import timezone

class Venta(models.Model):
    """Modelo principal de ventas"""
    
    ESTADOS = [
        ('PENDIENTE_BO', 'Pendiente Back Office'),
        ('PENDIENTE_AUDIO', 'Pendiente Audio'),
        ('AUDIO_REVISION', 'Audio en Revisión'),
        ('AUDIO_NO_CONFORME', 'Audio No Conforme'),
        ('PENDIENTE_INSTALACION', 'Pendiente Instalación'),
        ('EN_EJECUCION', 'En Ejecución'),
        ('INSTALADA', 'Instalada'),
        ('RECHAZADA', 'Rechazada'),
    ]
    
    GENEROS = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    
    # Datos registrados por el asesor
    asesor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='ventas_realizadas',
        limit_choices_to={'rol': 'ASESOR'}
    )
    modalidad = models.CharField(max_length=20, choices=[
        ('CALL_CENTER', 'Call Center'),
        ('CAMPO', 'Campo'),
    ])
    turno = models.CharField(max_length=10, choices=[
        ('MAÑANA', 'Mañana'),
        ('TARDE', 'Tarde'),
    ])
    
    # Datos del cliente
    cliente_nombre = models.CharField('Nombre del Cliente', max_length=200)
    cliente_dni = models.CharField('DNI', max_length=8)
    cliente_telefono = models.CharField('Teléfono', max_length=20)
    cliente_direccion = models.TextField('Dirección')
    cliente_correo = models.TextField('Correo')
    cliente_genero = models.CharField('Género', max_length=1, choices=GENEROS)
    
    # Datos del producto/servicio
    producto_servicio = models.CharField('Producto/Servicio', max_length=200)
    monto = models.DecimalField('Monto', max_digits=10, decimal_places=2)
    observaciones = models.TextField('Observaciones', blank=True)
    
    # Datos completados por Back Office (Jadira)
    sec = models.CharField('SEC', max_length=50, blank=True)
    sot = models.CharField('SOT', max_length=50, blank=True)
    fecha_instalacion_programada = models.DateField('Fecha Instalación Programada', null=True, blank=True)
    fecha_instalacion_real = models.DateField('Fecha Instalación Real', null=True, blank=True)
    
    # Control de estado
    estado = models.CharField(max_length=30, choices=ESTADOS, default='PENDIENTE_BO')
    motivo_rechazo = models.TextField('Motivo de Rechazo', blank=True)
    
    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ventas_modificadas'
    )
    
    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Venta #{self.id} - {self.cliente_nombre}"
    
    def puede_modificar_asesor(self):
        """El asesor solo puede modificar si está en ciertos estados"""
        return self.estado in ['PENDIENTE_BO', 'PENDIENTE_AUDIO']
    
    def puede_completar_backoffice(self):
        """Back office puede completar si está pendiente"""
        return self.estado == 'PENDIENTE_BO'


class NotificacionVenta(models.Model):
    """Notificaciones de cambios en ventas"""
    
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='notificaciones')
    usuario_destinatario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones_recibidas'
    )
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Notificación para {self.usuario_destinatario.username}"