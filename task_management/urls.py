from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Root → redirect to login
    path('', RedirectView.as_view(url='/login/', permanent=False)),

    # Auth (web login/logout)
    path('', include('dashboard.urls')),

    # JWT API endpoints
    path('api/auth/', include('accounts.urls')),
    path('api/tasks/', include('tasks.urls')),
]
