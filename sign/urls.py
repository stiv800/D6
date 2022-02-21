from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from .views import BaseRegisterView
from .views import upgrade_me

urlpatterns = [
    path('upgrade/', upgrade_me, name = 'upgrade'),
    path('login/', LoginView.as_view(template_name = 'login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name = 'logout.html'), name='logout'),
    path('signup/', BaseRegisterView.as_view(template_name = 'signup.html'), name='signup'),
]
