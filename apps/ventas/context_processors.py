from .models import NotificacionVenta

def notificaciones_pendientes(request):
    """Context processor para mostrar notificaciones en todas las páginas"""
    if request.user.is_authenticated:
        count = NotificacionVenta.objects.filter(
            usuario_destinatario=request.user,
            leida=False
        ).count()
        
        notificaciones = NotificacionVenta.objects.filter(
            usuario_destinatario=request.user,
            leida=False
        ).select_related('venta', 'venta__asesor')[:5]
        
        return {
            'notificaciones_count': count,
            'notificaciones_recientes': notificaciones,
        }
    
    return {
        'notificaciones_count': 0,
        'notificaciones_recientes': [],
    }