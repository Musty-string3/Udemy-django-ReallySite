from django.contrib import admin
from .models import *


class TagInline(admin.TabularInline):
    model = Article.tags.through

class ImageInline(admin.TabularInline):
    model = Image

class ArticleAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "text", "author", "is_public", "sell_flag", "price", "created_at", "updated_at")
    inlines = [TagInline, ImageInline]
    exclude = ['tags', ]

class ArticleTagAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "created_at")

class ImageAdmin(admin.ModelAdmin):
    list_display = ("id", "image", "article", "created_at")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "comment", "user", "article", "created_at")

class ArticleLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "article", "created_at")

class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "article", "price", "charge_type", "order_status", "created_at")

class UserItemAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "article", "charge_type", "created_at")

class ViewCountAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "article", "created_at")

class FollowAdmin(admin.ModelAdmin):
    list_display = ("id", "follower", "followed", "created_at")

class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user1", "user2", "created_at")

class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "text", "is_read", "created_at")

class MessageAttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "file_url", "file_type", "created_at")

class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "sender", "action_type", "article", "comment", "like", "follow", "is_read", "created_at")


admin.site.register(Article, ArticleAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(ArticleLike, ArticleLikeAdmin)
admin.site.register(ArticleTag, ArticleTagAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(UserItem, UserItemAdmin)
admin.site.register(ViewCount, ViewCountAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(MessageAttachment, MessageAttachmentAdmin)