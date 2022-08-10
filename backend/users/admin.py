import email
from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 
                    'email', 'is_staff', 'is_active',)
    ordering = ('email',)
    search_fields = ('username', 'email',)
    ordering = ('email',) 
    list_filter = ("username",'email',) 


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
