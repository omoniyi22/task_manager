from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Plan, Task
from django.utils import timezone

class StaffSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        if commit:
            user.save()
        return user

class PlanForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date()}),
        initial=timezone.now().date()
    )
    
    class Meta:
        model = Plan
        fields = ['date']

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'staff', 'admin_note']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['staff'].queryset = User.objects.filter(is_staff=True, is_superuser=False)

class StaffTaskUpdateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['status', 'staff_note']
        widgets = {
            'staff_note': forms.Textarea(attrs={'rows': 3}),
        }
        