from django.urls import path
from django.conf.urls import url
from .views import *


urlpatterns = [
    path('', NewsList.as_view()),
    path('<int:pk>/', NewsPost.as_view()),
    path('add/', PostCreateView.as_view(), name='post_create'),
    path('delete/<int:pk>/', PostDeleteView.as_view(), name='post_delete'),
    path('<int:pk>/edit/', PostUpdateView.as_view(), name='post_update'),
    path('upgrade/', upgrade_me, name = 'upgrade'),
    path('subscribe/', subscribe_me, name = 'subscribe'),
]