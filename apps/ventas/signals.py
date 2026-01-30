from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Venta, NotificacionVenta
from apps.usuarios.models import Usuario

@receiver(post_save, sender=Venta)
def crear_notificacion_venta(sender, instance, created, **kwargs):
    """Crea notificaciones cuando se crea o modifica una venta"""
    
    if created:
        # Nueva venta creada por asesor -> Notificar a Back Office
        usuarios_back_office = Usuario.objects.filter(rol='BACK_OFFICE', activo=True)
        
        for usuario in usuarios_back_office:
            NotificacionVenta.objects.create(
                venta=instance,
                usuario_destinatario=usuario,
                mensaje=f'Nueva venta #{instance.id} de {instance.asesor.get_full_name()} pendiente de completar'
            )
    
    else:
        # Venta modificada
        if instance.estado == 'PENDIENTE_AUDIO':
            # Back Office completó los datos -> Notificar al asesor
            NotificacionVenta.objects.create(
                venta=instance,
                usuario_destinatario=instance.asesor,
                mensaje=f'Venta #{instance.id} ha sido completada por Back Office. Fecha instalación: {instance.fecha_instalacion_programada}'
            )


@receiver(pre_save, sender=Venta)
def registrar_quien_modifico(sender, instance, **kwargs):
    """Registra quién hizo la última modificación"""
    if instance.pk:
        # Solo si ya existe (no es creación)
        pass  # El modificado_por se establece en la vista