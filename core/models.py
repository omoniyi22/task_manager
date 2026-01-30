from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class Plan(models.Model):
    date = models.DateField(unique=True, default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Plan for {self.date}"
    
    def save(self, *args, **kwargs):
        # Check if a plan already exists for this date
        if self.pk is None:  # Only for new instances
            if Plan.objects.filter(date=self.date).exists():
                raise ValidationError(f"A plan already exists for {self.date}")
        super().save(*args, **kwargs)

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]
    
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='tasks')
    staff = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_staff': True})
    name = models.CharField(max_length=200)
    admin_note = models.TextField(blank=True, null=True, verbose_name="Note by Admin")
    staff_note = models.TextField(blank=True, null=True, verbose_name="Note by Staff")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.staff.username}"