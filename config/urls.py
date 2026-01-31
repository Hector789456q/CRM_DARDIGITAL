from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.usuarios import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth (sin namespace para que login/logout/dashboard funcionen directo)
    path('', auth_views.login_view, name='login'),
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('dashboard/', auth_views.dashboard_view, name='dashboard'),

    # Usuarios (con namespace)
    path('', include('apps.usuarios.urls')),

    # Ventas
    path('ventas/', include('apps.ventas.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)