from django.urls import path, include

urlpatterns = [
    path('hydra/', include('hydra_auth.urls')),
]
