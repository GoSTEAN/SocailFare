from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Comment, FriendRequest, Conversation, Message
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .twitter_api import post_to_twitter
from django.db.models import Q
from django.contrib.auth import get_user_model

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
        
        try:
            # Create local post
            post = Post.objects.create(
                author=request.user,
                content=content,
                image=image
            )
            
            # Post to Twitter
            try:
                if image:
                    tweet = post_to_twitter(content, post.image.path)
                else:
                    tweet = post_to_twitter(content)
                
                # Save the Twitter post ID
                post.twitter_post_id = tweet.id_str
                post.save()
                
                messages.success(request, 'Posted successfully to both SocialFare and Twitter!')
            except Exception as e:
                messages.warning(request, f'Posted to SocialFare only. Twitter error: {str(e)}')
            
            return redirect('social:post_detail', pk=post.pk)
            
        except Exception as e:
            messages.error(request, f'Error creating post: {str(e)}')
            
    return render(request, 'social/post_form.html')

class LandingPageView(TemplateView):
    template_name = 'social/landing.html'

def home_or_landing(request):
    """Redirect to dashboard if logged in, otherwise show landing page"""
    if request.user.is_authenticated:
        return redirect('social:dashboard')
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
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        bio = request.POST.get('bio')
        profile_image = request.FILES.get('profile_image')
        
        # Update user
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        if hasattr(user, 'profile'):
            user.profile.bio = bio
            if profile_image:
                user.profile.image = profile_image
            user.profile.save()
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('social:profile')
        
    return render(request, 'social/edit_profile.html')
