from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Task

# Create your views here.

@login_required
def home(request):
    return render(request, 'tasks/home.html')

@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks/dashboard.html', {'tasks': tasks})

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

