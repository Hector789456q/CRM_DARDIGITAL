from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Usuario
from .forms import UsuarioForm, UsuarioEditForm


# ==================== LOGIN / LOGOUT ====================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.activo:
                login(request, user)
                messages.success(request, f'Bienvenido, {user.get_full_name()}')
                return redirect('dashboard')
            else:
                messages.error(request, 'Tu usuario está deshabilitado. Contacta al administrador.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente')
    return redirect('login')


# ==================== DASHBOARD ====================

@login_required
def dashboard_view(request):
    """Redirige al dashboard según el rol"""
    user = request.user

    if user.es_asesor():
        return redirect('ventas:asesor_dashboard')
    elif user.es_back_office():
        return redirect('ventas:jadira_dashboard')
    elif user.es_supervisor():
        return redirect('ventas:supervisor_dashboard')
    elif user.es_dueño():
        return redirect('ventas:dueño_dashboard')

    # Si es superuser/admin sin rol asignado, va a gestión de usuarios
    if user.is_superuser:
        return redirect('usuarios:lista_usuarios')

    return redirect('login')


# ==================== GESTIÓN DE USUARIOS ====================

@login_required
def lista_usuarios(request):
    """Lista de todos los usuarios"""
    # Solo Dueño o Superuser puede ver esto
    if not request.user.es_dueño() and not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para acceder a esta sección')
        return redirect('dashboard')

    # Filtros
    rol = request.GET.get('rol', '')
    buscar = request.GET.get('buscar', '')

    usuarios = Usuario.objects.all().order_by('-date_joined')

    if rol:
        usuarios = usuarios.filter(rol=rol)

    if buscar:
        usuarios = usuarios.filter(
            username__icontains=buscar
        ) | usuarios.filter(
            first_name__icontains=buscar
        ) | usuarios.filter(
            last_name__icontains=buscar
        )

    context = {
        'usuarios': usuarios,
        'roles': Usuario.ROLES,
        'filtros': {
            'rol': rol,
            'buscar': buscar,
        }
    }

    return render(request, 'usuarios/lista_usuarios.html', context)


@login_required
def crear_usuario(request):
    """Crear nuevo usuario"""
    if not request.user.es_dueño() and not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para acceder a esta sección')
        return redirect('dashboard')

    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Usuario {usuario.get_full_name()} creado correctamente')
            return redirect('usuarios:lista_usuarios')
    else:
        form = UsuarioForm()

    return render(request, 'usuarios/crear_usuario.html', {'form': form})


@login_required
def editar_usuario(request, usuario_id):
    """Editar usuario existente"""
    if not request.user.es_dueño() and not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para acceder a esta sección')
        return redirect('dashboard')

    usuario = get_object_or_404(Usuario, id=usuario_id)

    # No se puede editar a si mismo desde aquí
    if usuario == request.user:
        messages.warning(request, 'No puedes editarte a ti mismo desde aquí')
        return redirect('usuarios:lista_usuarios')

    if request.method == 'POST':
        form = UsuarioEditForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario {usuario.get_full_name()} actualizado correctamente')
            return redirect('usuarios:lista_usuarios')
    else:
        form = UsuarioEditForm(instance=usuario)

    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario': usuario})


@login_required
def deshabilitar_usuario(request, usuario_id):
    """Deshabilitar usuario sin eliminarlo"""
    if not request.user.es_dueño() and not request.user.is_superuser:
        messages.error(request, 'No tienes permisos')
        return redirect('dashboard')

    usuario = get_object_or_404(Usuario, id=usuario_id)

    # No deshabilitar al propio usuario
    if usuario == request.user:
        messages.error(request, 'No puedes deshabilitarte a ti mismo')
        return redirect('usuarios:lista_usuarios')

    # Alternar estado activo/inactivo
    if usuario.activo:
        usuario.activo = False
        usuario.save()
        messages.success(request, f'Usuario {usuario.get_full_name()} deshabilitado')
    else:
        usuario.activo = True
        usuario.save()
        messages.success(request, f'Usuario {usuario.get_full_name()} habilitado')

    return redirect('usuarios:lista_usuarios')