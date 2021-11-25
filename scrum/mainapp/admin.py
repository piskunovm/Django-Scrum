from django.contrib import admin

from lkapp.forms import PostCreationForm
from mainapp.models import Category, Article, Comments, Complaint, UserBan


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = PostCreationForm


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    pass


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    pass


@admin.register(UserBan)
class UserBanAdmin(admin.ModelAdmin):
    pass
