from django.shortcuts import get_object_or_404

from authapp.models import User
from mainapp.helpers.scores import get_count_post_likes, get_count_post_dislikes
from mainapp.models import Comments


def get_user(pk):
    return User.objects.get(id=pk)


def get_current_user(request):
    current_user = request.user
    return current_user


def get_comment(pk):
    comment = get_object_or_404(Comments, pk=pk)
    return comment


# Метод для формирования списка комментариев для каждой статьи с сортировкой по дате создания
# и ограничением по количеству.
def get_comments(pk):
    comments = Comments.objects.filter(article=pk).order_by("-created_at")
    return comments


def get_comment_for_complaint(pk):
    comment = get_object_or_404(Comments, pk=pk)
    return comment
