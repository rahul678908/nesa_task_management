from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/',  views.login_view,  name='login'),
    path('logout/', views.logout_view, name='logout'),

    # SuperAdmin
    path('superadmin/dashboard/',                            views.superadmin_dashboard,           name='superadmin-dashboard'),
    path('superadmin/users/create/',                         views.superadmin_create_user,          name='superadmin-create-user'),
    path('superadmin/users/<int:user_id>/delete/',           views.superadmin_delete_user,          name='superadmin-delete-user'),
    path('superadmin/users/<int:user_id>/role/',             views.superadmin_change_role,          name='superadmin-change-role'),
    path('superadmin/assign/',                               views.superadmin_assign_user_to_admin, name='superadmin-assign'),
    path('superadmin/admins/<int:admin_id>/permissions/',    views.superadmin_manage_permissions,   name='superadmin-manage-permissions'),
    path('superadmin/tasks/<int:task_id>/report/',           views.superadmin_task_report,          name='superadmin-task-report'),

    # Admin Panel
    path('admin-panel/dashboard/',                           views.admin_dashboard,    name='admin-dashboard'),
    path('admin-panel/tasks/create/',                        views.admin_create_task,  name='admin-create-task'),
    path('admin-panel/tasks/<int:task_id>/delete/',          views.admin_delete_task,  name='admin-delete-task'),
    path('admin-panel/tasks/<int:task_id>/report/',          views.admin_task_report,  name='admin-task-report'),
]
