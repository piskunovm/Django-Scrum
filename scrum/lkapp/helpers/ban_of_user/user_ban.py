from datetime import datetime, timedelta

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone

from scrum.settings import FOREVER
from authapp.models import User
from lkapp.helpers.alerts.alert import SaveAlert
from lkapp.helpers.ban_of_user import get_ban_obj
from lkapp.helpers.rating_author import author_rate_low_before_ban
from mainapp import helpers
from mainapp.models import UserBan



def ban_time(request):
    """ Время в time_options указано в минутах"""
    time_options = {
        '5 минут': 5,
        '30 минут': 30,
        '1 час': 60,
        '12 часов': 720,
        '1 сутки': 1440,
        '7 дней': 10080,
        '1 месяц': 40320,
        'навсегда': FOREVER,
    }

    created_at = datetime.now(timezone.utc)
    time = request.POST.get("ban_time")
    for option in time_options.keys():
        if time == option:
            time_of_ban = timedelta(minutes=time_options[time])
            ban_end_time = created_at + time_of_ban
            return ban_end_time


def set_user_ban(request):
    if request.method == "POST":
        try:
            moderator = helpers.get_current_user(request)
            ban = UserBan.objects.create(
                banned_user=User.objects.get(pk=int(request.POST.get("user_id"))),
                reason=request.POST.get("reason"),
                moderator_comment=request.POST.get("ban_description"),
                moderator_id=moderator.id,
                created_at=datetime.now(timezone.utc),
                ban_end_time=ban_time(request),
            )
            author_rate_low_before_ban(ban.banned_user)
            SaveAlert(action_user=request.user, alert_user=ban.banned_user, ban=ban, event_type="user_ban")
        except Exception:
            pass
    return HttpResponseRedirect(reverse("mainapp:profile_page", kwargs={"pk": int(request.POST.get("user_id"))}))


def set_user_unban(pk):
    ban = get_ban_obj(pk)
    ban.ban_end_time = datetime.now(timezone.utc)
    ban.save()
    return HttpResponseRedirect(reverse("mainapp:profile_page", kwargs={"pk": pk}))
