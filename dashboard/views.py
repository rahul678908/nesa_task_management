from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

from accounts.models import User, ADMIN_PERMISSION_CHOICES
from tasks.models import Task


# ── Decorators ─────────────────────────────────────────────────────────────────

def require_superadmin(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'superadmin':
            return HttpResponseForbidden("Access denied. SuperAdmin only.")
        return view_func(request, *args, **kwargs)
    return wrapper


def require_admin_or_superadmin(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in ('admin', 'superadmin'):
            return HttpResponseForbidden("Access denied. Admin or SuperAdmin only.")
        return view_func(request, *args, **kwargs)
    return wrapper


# ── Auth ───────────────────────────────────────────────────────────────────────

def login_view(request):
    # If already logged in, send to the right dashboard.
    # Only redirect if the user actually HAS a dashboard — prevents loop for 'user' role.
    if request.user.is_authenticated:
        if request.user.role == 'superadmin':
            return redirect('/superadmin/dashboard/')
        elif request.user.role == 'admin':
            return redirect('/admin-panel/dashboard/')
        # role == 'user' has no web dashboard; just show the login page normally

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            return render(request, 'auth/login.html', {'error': 'Please enter your username and password.'})

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            if user.role == 'superadmin':
                return redirect('/superadmin/dashboard/')
            elif user.role == 'admin':
                return redirect('/admin-panel/dashboard/')
            else:
                # Regular users only use the API, not the web panel
                return render(request, 'auth/login.html', {
                    'error': 'This panel is for Admins and SuperAdmins only. Use the API to access your tasks.'
                })
        return render(request, 'auth/login.html', {'error': 'Invalid username or password.'})

    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('/login/')


# ── SuperAdmin: Dashboard ──────────────────────────────────────────────────────

@login_required(login_url='/login/')
@require_superadmin
def superadmin_dashboard(request):
    context = {
        'users': User.objects.filter(role='user').select_related('assigned_admin'),
        'admins': User.objects.filter(role='admin'),
        'tasks': Task.objects.all().select_related('assigned_to', 'created_by'),
        'total_tasks': Task.objects.count(),
        'completed_tasks': Task.objects.filter(status='completed').count(),
        'pending_tasks': Task.objects.filter(status='pending').count(),
        'permission_choices': ADMIN_PERMISSION_CHOICES,
    }
    return render(request, 'superadmin/dashboard.html', context)


# ── SuperAdmin: User Management ────────────────────────────────────────────────

@login_required(login_url='/login/')
@require_superadmin
def superadmin_create_user(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        role     = request.POST.get('role', 'user')
        admin_id = request.POST.get('assigned_admin')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return redirect('/superadmin/users/create/')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('/superadmin/users/create/')

        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)

        if role == 'user' and admin_id:
            try:
                new_user.assigned_admin = User.objects.get(id=admin_id, role='admin')
            except User.DoesNotExist:
                pass

        new_user.save()
        messages.success(request, f'{role.capitalize()} "{username}" created successfully.')
        return redirect('/superadmin/dashboard/')

    return render(request, 'superadmin/create_user.html', {
        'admins': User.objects.filter(role='admin')
    })


@login_required(login_url='/login/')
@require_superadmin
def superadmin_delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.role == 'superadmin':
        messages.error(request, 'Cannot delete a SuperAdmin.')
        return redirect('/superadmin/dashboard/')
    user.delete()
    messages.success(request, f'"{user.username}" deleted.')
    return redirect('/superadmin/dashboard/')


@login_required(login_url='/login/')
@require_superadmin
def superadmin_change_role(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in ('user', 'admin') and user.role != 'superadmin':
            user.role = new_role
            if new_role == 'admin':
                user.assigned_admin = None
            else:
                user.admin_permissions = []
            user.save()
            messages.success(request, f'{user.username} is now a {new_role}.')
        else:
            messages.error(request, 'Invalid role or cannot modify superadmin.')
    return redirect('/superadmin/dashboard/')


@login_required(login_url='/login/')
@require_superadmin
def superadmin_assign_user_to_admin(request):
    if request.method == 'POST':
        user  = get_object_or_404(User, id=request.POST.get('user_id'), role='user')
        admin = get_object_or_404(User, id=request.POST.get('admin_id'), role='admin')
        user.assigned_admin = admin
        user.save()
        messages.success(request, f'{user.username} assigned to {admin.username}.')
    return redirect('/superadmin/dashboard/')


# ── SuperAdmin: Admin Permissions ──────────────────────────────────────────────

@login_required(login_url='/login/')
@require_superadmin
def superadmin_manage_permissions(request, admin_id):
    admin = get_object_or_404(User, id=admin_id, role='admin')

    if request.method == 'POST':
        granted = [
            key for key, _ in ADMIN_PERMISSION_CHOICES
            if request.POST.get(key)
        ]
        admin.admin_permissions = granted
        admin.save()
        messages.success(request, f'Permissions updated for {admin.username}.')
        return redirect('/superadmin/dashboard/')

    return render(request, 'superadmin/manage_permissions.html', {
        'admin': admin,
        'permission_choices': ADMIN_PERMISSION_CHOICES,
        'current_permissions': admin.admin_permissions or [],
    })


# ── SuperAdmin: Task Reports ───────────────────────────────────────────────────

@login_required(login_url='/login/')
@require_superadmin
def superadmin_task_report(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if task.status != 'completed':
        messages.error(request, 'Report only available for completed tasks.')
        return redirect('/superadmin/dashboard/')
    return render(request, 'superadmin/task_report.html', {'task': task})


# ── Admin Panel ────────────────────────────────────────────────────────────────

@login_required(login_url='/login/')
@require_admin_or_superadmin
def admin_dashboard(request):
    if request.user.role == 'superadmin':
        tasks = Task.objects.all().select_related('assigned_to', 'created_by')
        users = User.objects.filter(role='user')
    else:
        tasks = Task.objects.filter(
            assigned_to__assigned_admin=request.user
        ).select_related('assigned_to', 'created_by')
        users = User.objects.filter(assigned_admin=request.user)

    return render(request, 'admin/dashboard.html', {
        'tasks': tasks,
        'users': users,
        'total_tasks': tasks.count(),
        'completed_tasks': tasks.filter(status='completed').count(),
        'can_create_task':  request.user.has_admin_permission('can_create_task'),
        'can_delete_task':  request.user.has_admin_permission('can_delete_task'),
        'can_view_reports': request.user.has_admin_permission('can_view_reports'),
        'can_assign_task':  request.user.has_admin_permission('can_assign_task'),
    })


@login_required(login_url='/login/')
@require_admin_or_superadmin
def admin_create_task(request):
    if not request.user.has_admin_permission('can_create_task'):
        return HttpResponseForbidden("You don't have permission to create tasks.")

    users = (
        User.objects.filter(role='user')
        if request.user.role == 'superadmin'
        else User.objects.filter(assigned_admin=request.user)
    )

    if request.method == 'POST':
        title          = request.POST.get('title', '').strip()
        description    = request.POST.get('description', '').strip()
        assigned_to_id = request.POST.get('assigned_to')
        due_date       = request.POST.get('due_date') or None

        if not title or not assigned_to_id:
            messages.error(request, 'Title and assigned user are required.')
            return render(request, 'admin/create_task.html', {'users': users})

        assigned_user = get_object_or_404(User, id=assigned_to_id, role='user')

        if request.user.role == 'admin' and assigned_user.assigned_admin != request.user:
            return HttpResponseForbidden("You can only assign tasks to your own users.")

        if not request.user.has_admin_permission('can_assign_task'):
            return HttpResponseForbidden("You don't have permission to assign tasks.")

        Task.objects.create(
            title=title,
            description=description,
            assigned_to=assigned_user,
            created_by=request.user,
            due_date=due_date,
        )
        messages.success(request, f'Task "{title}" created.')
        return redirect('/admin-panel/dashboard/')

    return render(request, 'admin/create_task.html', {'users': users})


@login_required(login_url='/login/')
@require_admin_or_superadmin
def admin_delete_task(request, task_id):
    if not request.user.has_admin_permission('can_delete_task'):
        return HttpResponseForbidden("You don't have permission to delete tasks.")

    task = get_object_or_404(Task, id=task_id)

    if request.user.role == 'admin' and task.assigned_to.assigned_admin != request.user:
        return HttpResponseForbidden("You can only delete tasks for your own users.")

    task.delete()
    messages.success(request, f'Task "{task.title}" deleted.')
    return redirect('/admin-panel/dashboard/')


@login_required(login_url='/login/')
@require_admin_or_superadmin
def admin_task_report(request, task_id):
    if not request.user.has_admin_permission('can_view_reports'):
        return HttpResponseForbidden("You don't have permission to view reports.")

    task = get_object_or_404(Task, id=task_id)

    if request.user.role == 'admin' and task.assigned_to.assigned_admin != request.user:
        return HttpResponseForbidden("You can only view reports for your own users' tasks.")

    if task.status != 'completed':
        messages.error(request, 'Report only available for completed tasks.')
        return redirect('/admin-panel/dashboard/')

    return render(request, 'admin/task_report.html', {'task': task})