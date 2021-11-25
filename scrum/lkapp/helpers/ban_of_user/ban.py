from datetime import datetime, timezone

from lkapp.helpers.ban_of_user import get_ban_obj


def ban_is_active(pk):
    # используем время UTC
    # пытаемся получить объект БАН, из него получаем время окончания бана
    # тк у одного юзера мб несколько банов - берем последний
    try:
        obj = get_ban_obj(pk)
        end = obj.ban_end_time
    except Exception:
        # если запись не найдена, то возвращаем False (Бана нет)
        return False
    # если дата окончания бана больше сегодняшней возвращаем TRUE иначе False
    return end > datetime.now(timezone.utc)
