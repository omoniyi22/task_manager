from django.contrib import admin
from .models import Plan, Task

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['date', 'created_at', 'task_count']
    search_fields = ['date']
    readonly_fields = ['created_at', 'updated_at']
    
    def task_count(self, obj):
        return obj.tasks.count()
    task_count.short_description = 'Tasks'

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan', 'staff', 'status', 'created_at']
    list_filter = ['status', 'plan__date', 'staff']
    search_fields = ['name', 'admin_note', 'staff_note']
    readonly_fields = ['created_at', 'updated_at']