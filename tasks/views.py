from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import CustomUserCreationForm, TaskForm, TagForm
from django.contrib.auth.decorators import login_required
from .models import Task, Tag, Notification
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.urls import reverse_lazy
import time, json
from django.http import JsonResponse

# Create your views here.

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')

class CustomLogoutView(LogoutView):
    template_name = 'registration/logout.html'
    next_page = reverse_lazy('home')

@login_required
def home(request):
    return render(request, 'tasks/home.html')

# Dashboard

@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user)
    notifications = []
    unread_count = 0
    task_urgencies = []  # Lista de tuplas (task, urgency)

    # Procesar filtros si es una petición AJAX
    status_filter = request.GET.get('status', '')
    due_date_filter = request.GET.get('due_date', '')
    priority_filter = request.GET.get('priority', '')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        filtered_tasks = Task.objects.filter(user=request.user)
        if status_filter:
            filtered_tasks = filtered_tasks.filter(status=status_filter)
        if due_date_filter:
            filtered_tasks = filtered_tasks.filter(due_date__date=due_date_filter)
        if priority_filter:
            filtered_tasks = filtered_tasks.filter(priority=priority_filter)

        task_data = []
        for task in filtered_tasks:
            due_date_str = task.due_date.strftime('%Y-%m-%dT%H:%M')
            time_diff = (time.mktime(time.strptime(due_date_str, '%Y-%m-%dT%H:%M')) - 
                        time.mktime(time.strptime(time.strftime('%Y-%m-%dT%H:%M'), '%Y-%m-%dT%H:%M')))
            urgency = 'low'
            if time_diff <= 0:
                urgency = 'overdue'
            elif 0 < time_diff <= 86400:
                urgency = 'high'
            elif 86400 < time_diff <= 172800:
                urgency = 'medium'
            task_data.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'due_date': task.due_date.strftime('%Y-%m-%d'),
                'tags': [tag.name for tag in task.tags.all()],
                'urgency': urgency
            })
        return JsonResponse({'tasks': task_data})

    current_datetime = time.strftime('%Y-%m-%dT%H:%M')
    print(f"Current datetime: {current_datetime}")  # Depuración
    for task in tasks:
        due_date_str = task.due_date.strftime('%Y-%m-%dT%H:%M')
        print(f"Task: {task.title}, Due date: {due_date_str}")  # Depuración
        time_diff = (time.mktime(time.strptime(due_date_str, '%Y-%m-%dT%H:%M')) - 
                     time.mktime(time.strptime(current_datetime, '%Y-%m-%dT%H:%M')))
        print(f"Time difference (seconds): {time_diff}")  # Depuración
        if 0 < time_diff <= 86400:  # Menos de 24 horas
            notification, created = Notification.objects.get_or_create(
                task=task,
                defaults={'message': f'La tarea "{task.title}" vence en menos de 24 horas.'}
            )
            if created or not notification.is_read:
                notifications.append(notification)
                if not notification.is_read:
                    unread_count += 1
            print(f"Notification created/added for {task.title}, is_read: {notification.is_read}")  # Depuración
        # Calcular urgencia
        if time_diff <= 0:
            urgency = 'overdue'
        elif 0 < time_diff <= 86400:
            urgency = 'high'
        elif 86400 < time_diff <= 172800:
            urgency = 'medium'
        else:
            urgency = 'low'
        task_urgencies.append((task, urgency))  # Añadir tupla (task, urgency)
        print(f"Task: {task.title}, Urgency: {urgency}")  # Depuración

    return render(request, 'tasks/dashboard.html', {
        'tasks_with_urgencies': task_urgencies,
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
def mark_notification_as_read(request, notification_id):
    if request.method == 'POST':
        notification = get_object_or_404(Notification, id=notification_id, task__user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('dashboard')
    else:
        form = TaskForm(user=request.user)
    return render(request, 'tasks/create_task.html', {'form': form})


@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/edit_task.html', {'form': form, 'task': task})

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('dashboard')
    return render(request, 'tasks/delete_task.html', {'task': task})

@login_required
def create_tag(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            tag = form.save(commit=False)
            tag.created_by = request.user
            tag.save()
            return redirect('dashboard')
    else:
        form = TagForm()
    return render(request, 'tasks/create_tag.html', {'form': form})

@login_required
def update_task_status(request, task_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        task = get_object_or_404(Task, id=task_id, user=request.user)
        print(f"Recibido: task_id={task_id}, request.POST={request.POST}, request.body={request.body.decode('utf-8')}")  # Depuración
        # Parsear el cuerpo JSON manualmente
        try:
            body = json.loads(request.body.decode('utf-8'))
            new_status_label = body.get('status')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Cuerpo de la petición no válido'}, status=400)
        # Mapeo de etiquetas a valores internos
        status_map = {
            'Pendiente': 'pending',
            'En Progreso': 'in_progress',
            'Completada': 'completed'
        }
        if new_status_label in status_map:
            task.status = status_map[new_status_label]
            task.save()
            return JsonResponse({'success': True, 'status': new_status_label})  # Devuelve la etiqueta
        return JsonResponse({'success': False, 'error': 'Estado no válido'}, status=400)
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')                          # Redirige a la página principal después del registro
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'
