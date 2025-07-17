from django.urls import path
from . import views
from .views import (
    CustomLoginView, CustomLogoutView,
    CustomPasswordResetView, CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView, CustomPasswordResetCompleteView
)

urlpatterns = [
    path('register/', views.register, name='register'),                                     # Url para registrarse
    path('dashboard/', views.dashboard, name='dashboard'),                                  # Url para dashboard
    path('create_task/', views.create_task, name='create_task'),                            # Url para crear tarea
    path('edit_task/<int:task_id>/', views.edit_task, name='edit_task'),                    # Url para editar tarea
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),              # Url para eliminar tarea
    path('create_tag/', views.create_tag, name='create_tag'),                               # Url para crear etiqueta
    path('mark_notification_as_read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),   # Url para notificación
    path('update_task_status/<int:task_id>/', views.update_task_status, name='update_task_status'),                                # Url para actualizar estado de la tarea
    path('', views.home, name='home'),                                                      # Url para registrarse
    path('accounts/login/', CustomLoginView.as_view(), name='login'),                       # Url para iniciar sesión
    path('accounts/logout/', CustomLogoutView.as_view(), name='logout'),                    # Url para cerrar sesión
    path('accounts/password_reset/', CustomPasswordResetView.as_view(), name='password_reset'), # Url para resetear contraseña
    path('accounts/password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'), # Url resetear contraseña
    path('accounts/reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'), # URL para resetear contraseña
    path('accounts/reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),              # URL raíz
]