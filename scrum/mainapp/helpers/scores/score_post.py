from lkapp.helpers.alerts.alert import SaveAlert
from mainapp.helpers.post_rate import rating
from mainapp.models import Article, Score


def get_post(post_id):
    return Article.objects.get(pk=post_id)


def get_post_likes(user, post_id):
    return Score.objects.filter(user=user, article_id=post_id, score="like")


def get_post_dislikes(user, post_id):
    return Score.objects.filter(user=user, article_id=post_id, score="dislike")


def check_post_liked(user, post_id):
    if get_post_likes(user, post_id):
        return True
    else:
        return False


def check_post_disliked(user, post_id):
    if get_post_dislikes(user, post_id):
        return True
    else:
        return False


# Функция для оценки поста (новая)
def to_score_post(user, post_id, action):
    post = get_post(post_id)

    if action == "like":
        print(f"Оценка статьи, действие - {action}")
        if check_post_liked(user, post_id):
            Score.objects.get(user=user, article_id=post_id, score="like").delete()
        elif check_post_disliked(user, post_id):
            Score.objects.get(user=user, article_id=post_id, score="dislike").delete()
            like = Score.objects.create(user=user, article_id=post_id, score="like")
            SaveAlert(action_user=user, like=like, post=post, event_type="post_like")
        else:
            like = Score.objects.create(user=user, article_id=post_id, score="like")
            SaveAlert(action_user=user, like=like, post=post, event_type="post_like")
        rating(post)

    if action == "dislike":
        print(f"Оценка статьи, действие - {action}")
        if check_post_disliked(user, post_id):
            Score.objects.get(user=user, article_id=post_id, score="dislike").delete()
        elif check_post_liked(user, post_id):
            Score.objects.get(user=user, article_id=post_id, score="like").delete()
            dislike = Score.objects.create(user=user, article_id=post_id, score="dislike")
            SaveAlert(action_user=user, like=dislike, post=post, event_type="post_dislike")
        else:
            dislike = Score.objects.create(user=user, article_id=post_id, score="dislike")
            SaveAlert(action_user=user, like=dislike, post=post, event_type="post_dislike")
        rating(post)
