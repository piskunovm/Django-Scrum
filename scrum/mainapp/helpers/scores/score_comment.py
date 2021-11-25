from django.core.exceptions import ObjectDoesNotExist

from mainapp.helpers import get_comments
from mainapp.helpers.scores import Liked, Disliked
from mainapp.models import Score


def get_comment_like(user_id, comment_id):
    return Score.objects.filter(user=user_id, comment_id=comment_id, score="like")


def get_comment_dislike(user_id, comment_id):
    return Score.objects.filter(user=user_id, comment_id=comment_id, score="dislike")


def check_comment_liked(user_id, comment_id):
    if get_comment_like(user_id, comment_id):
        return True
    else:
        return False


def check_comment_disliked(user_id, comment_id):
    if get_comment_dislike(user_id, comment_id):
        return True
    else:
        return False


def to_score_comment(user, comment_id, action):

    if action == "like":
        print(f"Оценка комментария, действие - {action}")
        if check_comment_liked(user, comment_id):
            Score.objects.get(user=user, comment_id=comment_id, score="like").delete()
        elif check_comment_disliked(user, comment_id):
            Score.objects.get(user=user, comment_id=comment_id, score="dislike").delete()
            Score.objects.create(user=user, comment_id=comment_id, score="like")
        else:
            Score.objects.create(user=user, comment_id=comment_id, score="like")

    if action == "dislike":
        print(f"Оценка комментария, действие - {action}")
        if check_comment_disliked(user, comment_id):
            Score.objects.get(user=user, comment_id=comment_id, score="dislike").delete()
        elif check_comment_liked(user, comment_id):
            Score.objects.get(user=user, comment_id=comment_id, score="like").delete()
            Score.objects.create(user=user, comment_id=comment_id, score="dislike")
        else:
            Score.objects.create(user=user, comment_id=comment_id, score="dislike")


def read_comment_like(request, pk=None):
    comments = get_comments(pk)
    liked = []
    if request.user.is_authenticated:
        for comment in comments:
            try:
                Score.objects.get(user_id=request.user.id, comment_id=comment.id, score='like')
                liked.append(Liked(True, text=None, obj=comment))
            except ObjectDoesNotExist:
                liked.append(Liked(False, text=None, obj=comment))
        return liked
    return Liked(False, 0, "User don't authorized")


def read_comment_dislike(request, pk=None):
    comments = get_comments(pk)
    disliked = []
    if request.user.is_authenticated:
        for comment in comments:
            try:
                Score.objects.get(user_id=request.user.id, comment_id=comment.id, score='dislike')
                disliked.append(Disliked(True, text=None, obj=comment))
            except ObjectDoesNotExist:
                disliked.append(Disliked(False, text=None, obj=comment))
        return disliked
    return Disliked(False, 0, "User don't authorized")
