from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Comment, FriendRequest, Conversation, Message, Profile, Notification
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .twitter_api import post_to_twitter
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.http import JsonResponse

User = get_user_model()

class PostListView(ListView):
    model = Post
    template_name = 'social/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']

class PostDetailView(DetailView):
    model = Post
    template_name = 'social/post_detail.html'

@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        if content or image:
            post = Post.objects.create(
                author=request.user,
                content=content,
                image=image
            )
            # Create notification for new post to all friends
            for friend in request.user.friends.all():
                create_notification(request.user, friend, 'new_post', post)
            messages.success(request, 'Post created successfully!')
            return redirect('social:home')
    return render(request, 'social/create_post.html')

def home_or_landing(request):
    if request.user.is_authenticated:
        # Get all posts ordered by creation date (newest first)
        posts = Post.objects.all().order_by('-created_at')
        return render(request, 'social/home.html', {'posts': posts})
    else:
        # If not logged in, show landing page
        return render(request, 'social/landing.html')

class LandingPageView(TemplateView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('social:home')
        return render(request, 'social/landing.html')

class DashboardView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'social/dashboard.html'
    context_object_name = 'posts'
    ordering = ['-created_at']

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'social/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get('username')
        if username:
            # Viewing someone else's profile
            context['profile_user'] = get_object_or_404(User, username=username)
            context['is_own_profile'] = False
        else:
            # Viewing own profile
            context['profile_user'] = self.request.user
            context['is_own_profile'] = True
        return context

class FriendsView(LoginRequiredMixin, TemplateView):
    template_name = 'social/friends.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['friend_requests'] = FriendRequest.objects.filter(to_user=self.request.user)
        context['friends'] = self.request.user.friends.all()
        return context

class MessagesView(LoginRequiredMixin, TemplateView):
    template_name = 'social/messages.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['conversations'] = Conversation.objects.filter(participants=self.request.user)
        conversation_id = self.kwargs.get('conversation_id')
        if conversation_id:
            context['active_conversation'] = get_object_or_404(
                Conversation, 
                id=conversation_id, 
                participants=self.request.user
            )
        return context

@login_required
def search_users(request):
    query = request.GET.get('q', '')
    users = []
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id)  # Exclude the current user
    return render(request, 'social/search.html', {'users': users, 'query': query})

@login_required
def edit_profile(request):
    # Get or create profile
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        bio = request.POST.get('bio', '')
        profile_image = request.FILES.get('profile_image')
        
        # Update user
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()
        
        # Update profile
        profile.bio = bio
        if profile_image:
            profile.image = profile_image
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('social:profile')
    
    context = {
        'profile': profile
    }
    return render(request, 'social/edit_profile.html', context)

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
            # Create notification for comment
            create_notification(request.user, post.author, 'post_comment', post)
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Comment cannot be empty!')
            
    return redirect('social:post_detail', pk=post_id)

def simple_password_reset(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        User = get_user_model()
        
        try:
            user = User.objects.get(username=username)
            
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password has been reset successfully!')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match!')
        except User.DoesNotExist:
            messages.error(request, 'Username not found!')
            
    return render(request, 'social/password/simple_password_reset.html')

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Check if the user is the author of the post
    if post.author == request.user:
        post.delete()
        messages.success(request, 'Post deleted successfully!')
    else:
        messages.error(request, 'You cannot delete this post!')
        
    return redirect('social:home')

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Check if the user is the author of the post
    if post.author != request.user:
        messages.error(request, 'You cannot edit this post!')
        return redirect('social:home')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        
        # Update post content
        post.content = content
        
        # Update image if a new one is provided
        if image:
            post.image = image
            
        post.save()
        messages.success(request, 'Post updated successfully!')
        return redirect('social:post_detail', pk=post.id)
        
    return render(request, 'social/edit_post.html', {'post': post})

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
        # Create notification for post like
        create_notification(request.user, post.author, 'post_like', post)
    
    return JsonResponse({
        'likes_count': post.likes.count(),
        'liked': liked
    })

def create_notification(sender, recipient, notification_type, post=None):
    if sender != recipient:  # Don't create notifications for your own actions
        Notification.objects.create(
            sender=sender,
            recipient=recipient,
            notification_type=notification_type,
            post=post
        )

@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    friend_request, created = FriendRequest.objects.get_or_create(
        from_user=request.user,
        to_user=to_user
    )
    if created:
        # Create notification for friend request
        create_notification(request.user, to_user, 'friend_request')
        messages.success(request, 'Friend request sent!')
    else:
        messages.info(request, 'Friend request already sent!')
    return redirect('social:profile_detail', username=to_user.username)

@login_required
def notifications(request):
    # Mark all notifications as read
    request.user.notifications.filter(is_read=False).update(is_read=True)
    notifications = request.user.notifications.all()
    return render(request, 'social/notifications.html', {'notifications': notifications})
