from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    # Asesor
    path('asesor/dashboard/', views.asesor_dashboard, name='asesor_dashboard'),
    path('asesor/crear/', views.asesor_crear_venta, name='asesor_crear_venta'),
    path('asesor/mis-ventas/', views.asesor_mis_ventas, name='asesor_mis_ventas'),
    path('asesor/venta/<int:venta_id>/', views.asesor_detalle_venta, name='asesor_detalle_venta'),
    
    # Back Office (Jadira)
    path('jadira/dashboard/', views.jadira_dashboard, name='jadira_dashboard'),
    path('jadira/pendientes/', views.jadira_pendientes, name='jadira_pendientes'),
    path('jadira/completar/<int:venta_id>/', views.jadira_completar_venta, name='jadira_completar_venta'),
    
    # Notificaciones
    path('notificacion/<int:notificacion_id>/leida/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    path('notificaciones/marcar-todas/', views.marcar_todas_leidas, name='marcar_todas_leidas'),
    
    # Placeholders para futuros dashboards
    path('supervisor/dashboard/', views.asesor_dashboard, name='supervisor_dashboard'),  # Temporal
    path('dueño/dashboard/', views.asesor_dashboard, name='dueño_dashboard'),  # Temporal
]