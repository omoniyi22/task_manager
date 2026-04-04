from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import Http404, JsonResponse
from django.db.models import Q
from .models import Plan, Task
from .forms import StaffSignUpForm, PlanForm, TaskForm, StaffTaskUpdateForm
from django.core.exceptions import ValidationError

# Utility functions
def is_admin(user):
    return user.is_superuser

def is_staff_user(user):
    return user.is_staff and not user.is_superuser

# Authentication Views
def staff_signup(request):
    if request.method == 'POST':
        form = StaffSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('staff_dashboard')
    else:
        form = StaffSignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            elif user.is_staff:
                return redirect('staff_dashboard')
            else:
                return redirect('login')
        else:
            return render(request, 'registration/login.html', {'error': 'Invalid credentials'})
    return render(request, 'registration/login.html')




@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    today = timezone.now().date()
    
    # Initialize with defaults
    today_plan = None
    upcoming_plans = []
    recent_plans = []
    staff_users = []
    
    try:
        # Try to get today's plan
        try:
            today_plan = Plan.objects.get(date=today)
        except Plan.DoesNotExist:
            today_plan = None
        except Exception as e:
            # Handle database errors
            print(f"Error getting today's plan: {e}")
            today_plan = None
        
        # Get upcoming plans
        try:
            upcoming_plans = Plan.objects.filter(date__gt=today).order_by('date')[:5]
        except Exception as e:
            print(f"Error getting upcoming plans: {e}")
            upcoming_plans = []
        
        # Get recent plans
        try:
            recent_plans = Plan.objects.filter(date__lt=today).order_by('-date')[:5]
        except Exception as e:
            print(f"Error getting recent plans: {e}")
            recent_plans = []
        
        # Get staff users
        try:
            staff_users = User.objects.filter(is_staff=True, is_superuser=False)
        except Exception as e:
            print(f"Error getting staff users: {e}")
            staff_users = []
            
    except Exception as e:
        # Catch any other database errors
        print(f"Database error: {e}")
    
    context = {
        'today_plan': today_plan,
        'upcoming_plans': upcoming_plans,
        'recent_plans': recent_plans,
        'staff_users': staff_users,
        'total_staff': len(staff_users),
        'today': today,
    }
    return render(request, 'core/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def plan_list(request):
    plans = Plan.objects.all().order_by('-date')
    return render(request, 'core/plan_list.html', {'plans': plans})

@login_required
@user_passes_test(is_admin)
def plan_create(request):
    if request.method == 'POST':
        form = PlanForm(request.POST)
        if form.is_valid():
            try:
                plan = form.save()
                return redirect('plan_detail', plan_id=plan.id)
            except ValidationError as e:
                form.add_error('date', e)
    else:
        form = PlanForm()
    return render(request, 'core/plan_create.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def plan_detail(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    
    if request.method == 'POST':
        if 'delete_task' in request.POST:
            task_id = request.POST.get('task_id')
            task = get_object_or_404(Task, id=task_id, plan=plan)
            task.delete()
            return redirect('plan_detail', plan_id=plan.id)
        
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.plan = plan
            task.save()
            return redirect('plan_detail', plan_id=plan.id)
    else:
        form = TaskForm()
    
    tasks = plan.tasks.all()
    return render(request, 'core/plan_detail.html', {
        'plan': plan,
        'tasks': tasks,
        'form': form,
    })

@login_required
@user_passes_test(is_admin)
def delete_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    if request.method == 'POST':
        plan.delete()
        return redirect('plan_list')
    return render(request, 'core/plan_confirm_delete.html', {'plan': plan})

# Staff Views
@login_required
@user_passes_test(is_staff_user)
def staff_dashboard(request):
    today = timezone.now().date()
    
    try:
        today_plan = Plan.objects.get(date=today)
        my_tasks = today_plan.tasks.filter(staff=request.user)
    except Plan.DoesNotExist:
        today_plan = None
        my_tasks = []
    
    # Get tasks from other plans
    other_tasks = Task.objects.filter(
        staff=request.user
    ).exclude(
        plan__date=today
    ).order_by('-plan__date')[:10]
    
    context = {
        'today_plan': today_plan,
        'my_tasks': my_tasks,
        'other_tasks': other_tasks,
    }
    return render(request, 'core/staff_dashboard.html', context)

@login_required
@user_passes_test(is_staff_user)
def staff_plan_detail(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    tasks = plan.tasks.filter(staff=request.user)
    
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        task = get_object_or_404(Task, id=task_id, staff=request.user)
        form = StaffTaskUpdateForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('staff_plan_detail', plan_id=plan.id)
    else:
        form = StaffTaskUpdateForm()
    
    return render(request, 'core/staff_plan_detail.html', {
        'plan': plan,
        'tasks': tasks,
        'form': form,
    })

@login_required
@user_passes_test(is_staff_user)
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, staff=request.user)
    
    if request.method == 'POST':
        form = StaffTaskUpdateForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('staff_plan_detail', plan_id=task.plan.id)
    else:
        form = StaffTaskUpdateForm(instance=task)
    
    return render(request, 'core/task_update.html', {
        'task': task,
        'form': form,
    })

# Common Views
@login_required
def dashboard(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    elif request.user.is_staff:
        return redirect('staff_dashboard')
    else:
        return redirect('login')