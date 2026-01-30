from django.contrib import admin
from .models import Venta, NotificacionVenta

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'cliente_nombre', 'asesor', 'estado', 'monto',
        'fecha_instalacion_programada', 'fecha_creacion'
    ]
    list_filter = ['estado', 'modalidad', 'turno', 'fecha_creacion']
    search_fields = ['cliente_nombre', 'cliente_dni', 'cliente_telefono']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    
    fieldsets = (
        ('Información del Asesor', {
            'fields': ('asesor', 'modalidad', 'turno')
        }),
        ('Datos del Cliente', {
            'fields': ('cliente_nombre', 'cliente_dni', 'cliente_telefono', 
                      'cliente_direccion','cliente_correo' , 'cliente_genero')
        }),
        ('Producto/Servicio', {
            'fields': ('producto_servicio', 'monto', 'observaciones')
        }),
        ('Datos de Back Office', {
            'fields': ('sec', 'sot', 'fecha_instalacion_programada', 'fecha_instalacion_real')
        }),
        ('Estado', {
            'fields': ('estado', 'motivo_rechazo')
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_modificacion', 'modificado_por'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NotificacionVenta)
class NotificacionVentaAdmin(admin.ModelAdmin):
    list_display = ['id', 'venta', 'usuario_destinatario', 'leida', 'fecha_creacion']
    list_filter = ['leida', 'fecha_creacion']
    search_fields = ['venta__cliente_nombre', 'usuario_destinatario__username']