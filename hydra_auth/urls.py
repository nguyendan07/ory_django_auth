from django.urls import path
from . import views

urlpatterns = [
    # Login, Consent, and Logout endpoints
    path('login', views.login_view, name='login'),
    path('login/reject', views.login_reject, name='login_reject'),
    path('consent', views.consent_view, name='consent'),
    path('consent/reject', views.consent_reject, name='consent_reject'),
    path('logout', views.logout_view, name='logout'),
    path('logout/reject', views.logout_reject, name='logout_reject'),
    
    # OAuth2 Client Management endpoints
    path('clients/', views.client_list, name='client_list'),
    path('clients/create/', views.client_create, name='client_create'),
    path('clients/<str:client_id>/update/', views.client_update, name='client_update'),
    path('clients/<str:client_id>/delete/', views.client_delete, name='client_delete'),
]
