from django.contrib import admin
from .models import *

class TagInline(admin.TabularInline):
    model = Article.tags.through

class ArticleAdmin(admin.ModelAdmin):
    inlines = [TagInline]
    exclude = ['tags', ]

admin.site.register(Article, ArticleAdmin)
admin.site.register(Comment)
admin.site.register(ArticleLike)
admin.site.register(ArticleTag)
admin.site.register(Order)
admin.site.register(UserItem)
admin.site.register(ViewCount)
admin.site.register(Follow)
