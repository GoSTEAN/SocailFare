from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, Post, Comment, FriendRequest, Conversation, Message

# Register your models
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(FriendRequest)
admin.site.register(Conversation)
admin.site.register(Message)
