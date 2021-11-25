from django.core.exceptions import ObjectDoesNotExist, FieldError

from authapp.models import User


def deactivate_user(request):
    try:
        user = User.objects.get(user_id=request.user.id)
        user.is_active = False
        user.save()
        return True
    except ObjectDoesNotExist:
        return False
    except FieldError:
        return False