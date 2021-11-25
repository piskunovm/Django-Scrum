# Рейтинг статьи
from mainapp.helpers import get_count_post_likes, get_count_post_dislikes


def rating(post):
    if get_count_post_likes(post.id) + get_count_post_dislikes(post.id) != 0:
        post.rating = (get_count_post_likes(post.id) - get_count_post_dislikes(post.id)) / (get_count_post_likes(post.id) + get_count_post_dislikes(post.id)) * 10
    else:
        post.rating = 0
    post.save()
    return post.rating
