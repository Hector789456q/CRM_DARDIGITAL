from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
                messages.success(request, f'Bienvenido {user.get_full_name()}')
                return redirect('dashboard')
            else:
                messages.error(request, 'Tu usuario está deshabilitado')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente')
    return redirect('login')

@login_required
def dashboard_view(request):
    """Redirige al dashboard según el rol del usuario"""
    user = request.user
    
    if user.es_asesor():
        return redirect('ventas:asesor_dashboard')
    elif user.es_back_office():
        return redirect('ventas:jadira_dashboard')
    elif user.es_supervisor():
        return redirect('ventas:supervisor_dashboard')
    elif user.es_dueño():
        return redirect('ventas:dueño_dashboard')
    
    return render(request, 'dashboard.html')