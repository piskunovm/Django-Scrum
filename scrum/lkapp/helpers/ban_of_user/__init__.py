from mainapp.models import UserBan


def get_ban_obj(pk):
    return UserBan.objects.filter(banned_user_id=pk).order_by("-created_at").first()