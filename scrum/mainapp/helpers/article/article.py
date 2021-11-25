from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from mainapp.models import Article, Category


def get_article(pk, *args, **kwargs):
    if "status" in kwargs:
        post = get_object_or_404(Article, pk=pk, status=kwargs["status"])
    else:
        post = get_object_or_404(Article, pk=pk)
    return post


def get_articles(category=None, sorted_by="-published_at"):
    try:
        if not category:
            articles = Article.objects.filter(status="published").order_by(sorted_by)
        else:
            articles = Article.objects.filter(status="published", category=category).order_by(sorted_by)
        return articles
    except ObjectDoesNotExist:
        return False


def get_count_published_posts(user_id):
    return Article.objects.filter(author=user_id, status="published").count()


def get_category_list():
    category_id = Article.objects.filter(status="published").values_list("category_id")
    categories = Category.objects.all().filter(id__in=category_id)
    return categories


def get_list_of_sorting_criteria_for_articles():
    return {
        "&#8593; Дата публикации": "published_at",
        "&#8595; Дата публикации": "-published_at",
        "&#8593; Рейтинг": "rating",
        "&#8595; Рейтинг": "-rating",
    }
