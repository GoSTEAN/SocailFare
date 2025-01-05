from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    path('', views.home_or_landing, name='home'),
    path('landing/', views.LandingPageView.as_view(), name='landing'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile_detail'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('post/create/', views.create_post, name='post_create'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('friends/', views.FriendsView.as_view(), name='friends'),
    path('messages/', views.MessagesView.as_view(), name='messages'),
    path('search/', views.search_users, name='search'),
    path('password/reset/', views.simple_password_reset, name='simple_password_reset'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('notifications/', views.notifications, name='notifications'),
]
