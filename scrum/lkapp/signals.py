import threading
from functools import wraps

from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from post_office import mail

from .helpers.alerts import get_email, get_mail_settings
from .helpers.alerts.mail_alert import mail_content
from .models import Alert, UserSettings, UserSettingsLog


def thread(f):
    """ This decorator executes a function in a Thread"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        thr = threading.Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper


@thread
@receiver(post_save, sender=Alert)
def mail_sender(instance, **kwargs):
    """settings.SEND_EMAIL не убирать!!!! Иначе при fill_db на каждый новый объект в базе отправляться сообщение"""
    if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD and settings.SEND_EMAIL:
        obj = mail_content(instance)
        if get_mail_settings(obj.alert_user_id):
            mail.send(get_email(obj.alert_user_id),
                      settings.EMAIL_HOST_USER,
                      template='default_email',
                      context={'obj': obj})
    else:
        print("Can't send email without user and password")

#
# @receiver(pre_save, sender=UserSettings)
# def user_log_settings(instance, **kwargs):
#     for setting in instance:
#         if setting.__name__ != 'user_id':
#             current_settings = UserSettings.objects.get(id=instance.user_id)
#             if setting != current_settings[f'{setting.__name__}']:
#                 UserSettingsLog.objects.create(
#                     user_id=instance.user_id,
#                     switched_setting=f'changed {setting.__name__} on {setting}'
#                 )