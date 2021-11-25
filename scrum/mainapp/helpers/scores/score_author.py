from lkapp.helpers.alerts.alert import SaveAlert
from lkapp.helpers.rating_author import author_rate_up_before_liked, author_rate_down_before_disliked
from mainapp.models import Score


def get_count_user_likes(author_id):
    return Score.objects.filter(score_user_id=author_id, score="like").count()


def get_count_user_dislikes(author_id):
    return Score.objects.filter(score_user_id=author_id, score="dislike").count()


def get_user_like(user_id, author_id):
    return Score.objects.filter(user=user_id, score_user=author_id, score="like")


def get_user_dislike(user_id, author_id):
    return Score.objects.filter(user=user_id, score_user=author_id, score="dislike")


def check_user_liked(user_id, author_id):
    if get_user_like(user_id, author_id):
        return True
    else:
        return False


def check_user_disliked(user_id, author_id):
    if get_user_dislike(user_id, author_id):
        return True
    else:
        return False


def to_score(user, author_user, action):

    if action == "like":
        print(f"Оценка автора, действие - {action}")
        if check_user_liked(user, author_user):
            Score.objects.get(user=user, score_user=author_user, score="like").delete()
        elif check_user_disliked(user, author_user):
            Score.objects.get(user=user, score_user=author_user, score="dislike").delete()
            like = Score.objects.create(user=user, score_user=author_user, score="like")
            author_rate_up_before_liked(author_user)
            SaveAlert(action_user=user, like=like, event_type="author_like")
        else:
            like = Score.objects.create(user=user, score_user=author_user, score="like")
            author_rate_up_before_liked(author_user)
            SaveAlert(action_user=user, like=like, event_type="author_like")

    if action == "dislike":
        print(f"Оценка автора, действие - {action}")
        if check_user_disliked(user, author_user):
            Score.objects.get(user=user, score_user=author_user, score="dislike").delete()
        elif check_user_liked(user, author_user):
            Score.objects.get(user=user, score_user=author_user, score="like").delete()
            dislike = Score.objects.create(user=user, score_user=author_user, score="dislike")
            author_rate_down_before_disliked(author_user)
            SaveAlert(action_user=user, like=dislike, event_type="author_dislike")
        else:
            dislike = Score.objects.create(user=user, score_user=author_user, score="dislike")
            author_rate_down_before_disliked(author_user)
            SaveAlert(action_user=user, like=dislike, event_type="author_dislike")
