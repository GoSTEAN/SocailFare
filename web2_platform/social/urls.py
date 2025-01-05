from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    # Landing/Home page
    path('', views.home_or_landing, name='landing'),
    
    # Dashboard and Profile
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),  # Default profile (current user)
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile_detail'),  # Other user's profile
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Friends and Messages
    path('friends/', views.FriendsView.as_view(), name='friends'),
    path('messages/', views.MessagesView.as_view(), name='messages'),
    path('messages/<int:conversation_id>/', views.MessagesView.as_view(), name='conversation'),
    
    # Search
    path('search/', views.search_users, name='search'),
    
    # Posts
    path('post/new/', views.create_post, name='post_create'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
]
