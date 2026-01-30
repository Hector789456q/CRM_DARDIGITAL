from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Venta, NotificacionVenta
from .forms import VentaAsesorForm, VentaBackOfficeForm
from apps.usuarios.models import Usuario
from django.utils import timezone


# ==================== VISTAS DE ASESOR ====================

@login_required
def asesor_dashboard(request):
    """Dashboard principal del asesor"""
    if not request.user.es_asesor():
        messages.error(request, 'No tienes permisos para acceder a esta sección')
        return redirect('dashboard')
    
    # Estadísticas del asesor
    mis_ventas = Venta.objects.filter(asesor=request.user)
    
    stats = {
        'total_ventas': mis_ventas.count(),
        'pendientes_bo': mis_ventas.filter(estado='PENDIENTE_BO').count(),
        'pendientes_instalacion': mis_ventas.filter(estado='PENDIENTE_INSTALACION').count(),
        'instaladas': mis_ventas.filter(estado='INSTALADA').count(),
        'rechazadas': mis_ventas.filter(estado='RECHAZADA').count(),
    }
    
    # Últimas 5 ventas
    ultimas_ventas = mis_ventas[:5]
    
    # Notificaciones no leídas
    notificaciones = NotificacionVenta.objects.filter(
        usuario_destinatario=request.user,
        leida=False
    )[:5]
    
    context = {
        'stats': stats,
        'ultimas_ventas': ultimas_ventas,
        'notificaciones': notificaciones,
    }
    
    return render(request, 'ventas/asesor_dashboard.html', context)


@login_required
def asesor_crear_venta(request):
    """Formulario para crear una nueva venta"""
    if not request.user.es_asesor():
        messages.error(request, 'No tienes permisos para acceder a esta sección')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = VentaAsesorForm(request.POST)
        if form.is_valid():
            venta = form.save(commit=False)
            venta.asesor = request.user
            venta.estado = 'PENDIENTE_BO'
            venta.modificado_por = request.user
            venta.save()
            
            messages.success(request, f'Venta #{venta.id} registrada correctamente. Back Office será notificado.')
            return redirect('ventas:asesor_mis_ventas')
    else:
        # Pre-llenar modalidad y turno del asesor
        initial_data = {
            'modalidad': request.user.modalidad if request.user.modalidad != 'AMBAS' else None,
            'turno': request.user.turno if request.user.turno != 'AMBOS' else None,
        }
        form = VentaAsesorForm(initial=initial_data)
    
    return render(request, 'ventas/asesor_crear_venta.html', {'form': form})


@login_required
def asesor_mis_ventas(request):
    """Listado de todas las ventas del asesor"""
    if not request.user.es_asesor():
        messages.error(request, 'No tienes permisos para acceder a esta sección')
        return redirect('dashboard')
    
    # Filtros
    estado = request.GET.get('estado', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    buscar = request.GET.get('buscar', '')
    
    ventas = Venta.objects.filter(asesor=request.user)
    
    if estado:
        ventas = ventas.filter(estado=estado)
    
    if fecha_desde:
        ventas = ventas.filter(fecha_creacion__date__gte=fecha_desde)
    
    if fecha_hasta:
        ventas = ventas.filter(fecha_creacion__date__lte=fecha_hasta)
    
    if buscar:
        ventas = ventas.filter(
            Q(cliente_nombre__icontains=buscar) |
            Q(cliente_dni__icontains=buscar) |
            Q(cliente_telefono__icontains=buscar)
        )
    
    # Paginación
    paginator = Paginator(ventas, 20)
    page = request.GET.get('page', 1)
    ventas_paginadas = paginator.get_page(page)
    
    context = {
        'ventas': ventas_paginadas,
        'estados': Venta.ESTADOS,
        'filtros': {
            'estado': estado,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'buscar': buscar,
        }
    }
    
    return render(request, 'ventas/asesor_mis_ventas.html', context)


@login_required
def asesor_detalle_venta(request, venta_id):
    """Ver detalle de una venta específica"""
    venta = get_object_or_404(Venta, id=venta_id)
    
    # Verificar que sea su venta
    if not request.user.es_asesor() or venta.asesor != request.user:
        messages.error(request, 'No tienes permisos para ver esta venta')
        return redirect('ventas:asesor_mis_ventas')
    
    # Marcar notificaciones como leídas
    NotificacionVenta.objects.filter(
        venta=venta,
        usuario_destinatario=request.user,
        leida=False
    ).update(leida=True)
    
    return render(request, 'ventas/asesor_detalle_venta.html', {'venta': venta})


# ==================== VISTAS DE BACK OFFICE (JADIRA) ====================

@login_required
def jadira_dashboard(request):
    """Dashboard de Back Office"""
    if not request.user.es_back_office():
        messages.error(request, 'No tienes permisos para acceder a esta sección')
        return redirect('dashboard')
    
    # Estadísticas
    stats = {
        'pendientes': Venta.objects.filter(estado='PENDIENTE_BO').count(),
        'completadas_hoy': Venta.objects.filter(
            estado='PENDIENTE_AUDIO',
            fecha_modificacion__date=timezone.now().date()
        ).count(),
        'total_procesadas': Venta.objects.exclude(estado='PENDIENTE_BO').count(),
    }
    
    # Ventas pendientes recientes
    ventas_pendientes = Venta.objects.filter(estado='PENDIENTE_BO')[:10]
    
    # Notificaciones no leídas
    notificaciones = NotificacionVenta.objects.filter(
        usuario_destinatario=request.user,
        leida=False
    )[:5]
    
    context = {
        'stats': stats,
        'ventas_pendientes': ventas_pendientes,
        'notificaciones': notificaciones,
    }
    
    return render(request, 'ventas/jadira_dashboard.html', context)


@login_required
def jadira_pendientes(request):
    """Listado de ventas pendientes de completar"""
    if not request.user.es_back_office():
        messages.error(request, 'No tienes permisos para acceder a esta sección')
        return redirect('dashboard')
    
    # Filtros
    asesor_id = request.GET.get('asesor', '')
    buscar = request.GET.get('buscar', '')
    
    ventas = Venta.objects.filter(estado='PENDIENTE_BO').select_related('asesor')
    
    if asesor_id:
        ventas = ventas.filter(asesor_id=asesor_id)
    
    if buscar:
        ventas = ventas.filter(
            Q(cliente_nombre__icontains=buscar) |
            Q(cliente_dni__icontains=buscar)
        )
    
    # Paginación
    paginator = Paginator(ventas, 20)
    page = request.GET.get('page', 1)
    ventas_paginadas = paginator.get_page(page)
    
    # Lista de asesores para filtro
    asesores = Usuario.objects.filter(rol='ASESOR', activo=True)
    
    context = {
        'ventas': ventas_paginadas,
        'asesores': asesores,
        'filtros': {
            'asesor': asesor_id,
            'buscar': buscar,
        }
    }
    
    return render(request, 'ventas/jadira_pendientes.html', context)


@login_required
def jadira_completar_venta(request, venta_id):
    """Completar los 3 campos de una venta"""
    if not request.user.es_back_office():
        messages.error(request, 'No tienes permisos para acceder a esta sección')
        return redirect('dashboard')
    
    venta = get_object_or_404(Venta, id=venta_id)
    
    if not venta.puede_completar_backoffice():
        messages.error(request, 'Esta venta ya fue procesada')
        return redirect('ventas:jadira_pendientes')
    
    if request.method == 'POST':
        form = VentaBackOfficeForm(request.POST, instance=venta)
        if form.is_valid():
            venta = form.save(commit=False)
            venta.estado = 'PENDIENTE_AUDIO'
            venta.modificado_por = request.user
            venta.save()
            
            messages.success(request, f'Venta #{venta.id} completada. El asesor {venta.asesor.get_full_name()} será notificado.')
            return redirect('ventas:jadira_pendientes')
    else:
        form = VentaBackOfficeForm(instance=venta)
    
    # Marcar notificación como leída
    NotificacionVenta.objects.filter(
        venta=venta,
        usuario_destinatario=request.user,
        leida=False
    ).update(leida=True)
    
    context = {
        'form': form,
        'venta': venta,
    }
    
    return render(request, 'ventas/jadira_completar_venta.html', context)


# ==================== VISTAS DE NOTIFICACIONES ====================

@login_required
def marcar_notificacion_leida(request, notificacion_id):
    """Marcar una notificación como leída"""
    notificacion = get_object_or_404(
        NotificacionVenta,
        id=notificacion_id,
        usuario_destinatario=request.user
    )
    notificacion.leida = True
    notificacion.save()
    
    return redirect('ventas:asesor_detalle_venta', venta_id=notificacion.venta.id)


@login_required
def marcar_todas_leidas(request):
    """Marcar todas las notificaciones como leídas"""
    NotificacionVenta.objects.filter(
        usuario_destinatario=request.user,
        leida=False
    ).update(leida=True)
    
    messages.success(request, 'Todas las notificaciones marcadas como leídas')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))