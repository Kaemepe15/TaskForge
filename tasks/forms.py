from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Task, Tag
import time

class CustomUserCreationForm(UserCreationForm):                    # Formulario para la creación de usuario
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")    # Campos del formulario

    def save(self, commit=True):                                    # Condición para guardar el usuario, si el correo no se encuentra registrados
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'due_date', 'tags', 'background_color']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'background_color': forms.TextInput(attrs={'type': 'color'}),
            'tags': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TaskForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['tags'].queryset = Tag.objects.filter(created_by=user)

    def clean_due_date(self):
        due_date = self.cleaned_data['due_date']
        if due_date:
            # Obtener la fecha y hora actual como cadena en formato YYYY-MM-DDTHH:MM
            current_datetime = time.strftime('%Y-%m-%dT%H:%M')
            # Convertir due_date a cadena en el mismo formato
            due_date_str = due_date.strftime('%Y-%m-%dT%H:%M')
            if due_date_str < current_datetime:
                raise forms.ValidationError("La fecha límite no puede ser anterior a la fecha actual.")
        return due_date

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']