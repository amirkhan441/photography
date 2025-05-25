from django.contrib import admin
from .models import Photo, Comment, Like

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'like_count', 'comment_count')
    list_filter = ('created_at', 'user')
    search_fields = ('title', 'description', 'user__username')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'user', 'photo', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('text', 'user__username', 'photo__title')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'photo', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'photo__title')
