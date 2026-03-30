from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),                     # Page 1: Landing Page
    path('register/', views.register_student, name='register'), # Page 2: Registration
    path('attendance/', views.live_attendance, name='attendance'), # Page 3: Live Feed
    
    path('video_feed/', views.video_feed, name='video_feed'), # Background video processor
    path('records/', views.view_records, name='records'),
]