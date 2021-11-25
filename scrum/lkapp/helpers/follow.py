from django.core.exceptions import ObjectDoesNotExist

from authapp.models import User
from mainapp.helpers import get_current_user


def get_followers(user_id):
    try:
        followers = User.objects.get(id=user_id).followers.all()
        return followers
    except ObjectDoesNotExist:
        return False


def check_follow(request, author_pk):
    user = get_current_user(request)
    author_user = User.objects.get(id=author_pk)
    if user in author_user.followers.prefetch_related().all():
        return True
    else:
        return False
