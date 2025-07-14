from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Task(models.Model):                       # Modelo para las tareas
    STATUS_CHOICES = [                          # Estado de las tareas
        ('pending', 'Pendiente'),               # Estado - pendiente
        ('in_progress', 'En Progreso'),         # Estado - en progreso
        ('completed', 'Completada'),            # Estado - completada
    ]

    PRIORITY_CHOICES = [                        # Nivel de prioridad
        ('low', 'Baja'),                        # Nivel - baja
        ('medium', 'Media'),                    # Nivel - media
        ('high', 'Alta'),                       # Nivel - alta
    ]

    # Campos de las tareas (Usuario, titulo, descripción, estado, prioridad, fecha, etiquetas, crear, actualizar)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateTimeField()
    tags = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title