from authapp.models import User

MAX_RATING_AUTHOR = 10
MIN_RATING_AUTHOR = 0
STEP_UP_RATE_BEFORE_PUBLICATE = 1
STEP_UP_RATE_BEFORE_LIKED = 0.1
STEP_DOWN_RATE_BEFORE_DISLIKED = 0.1
STEP_DOWN_RATE_BEFORE_COMPLAIN = 5
STEP_DOWN_RATE_BEFORE_BAN = 5
RATE_FOR_PUBLICATED_WITHOUT_MODERATING = 7


# Возвращает рейтинг автора
def get_rate_author(id):
    return round(User.objects.get(id=id).author_rating, 2)


# Функция увеличивает рейтинг автора после публикации поста.
def author_rate_up_before_publicated(user, max_rait=MAX_RATING_AUTHOR, step_up=STEP_UP_RATE_BEFORE_PUBLICATE):
    author = User.objects.get(id=user)
    author.author_rating += step_up
    author.author_rating = round(author.author_rating, 2)
    if author.author_rating > max_rait:
        author.author_rating = max_rait
        author.save()
    else:
        author.save()
    print(f'Рейтинг автора увеличился на {step_up}')


# Функция увеличивает рейтинг автора после лайка пользователем автора.
def author_rate_up_before_liked(author, max_rait=MAX_RATING_AUTHOR, step_up=STEP_UP_RATE_BEFORE_LIKED):
    author.author_rating += step_up
    author.author_rating = round(author.author_rating, 2)
    if author.author_rating > max_rait:
        author.author_rating = max_rait
        author.save()
    else:
        author.save()
    print(f'Рейтинг автора увеличился на {step_up}')


# Функция уменьшает рейтинг автора после дизлайка пользователем автора.
def author_rate_down_before_disliked(author, min_rate=MIN_RATING_AUTHOR, step_down=STEP_DOWN_RATE_BEFORE_DISLIKED):
    author.author_rating -= step_down
    author.author_rating = round(author.author_rating, 2)
    if author.author_rating < min_rate:
        author.author_rating = min_rate
        author.save()
    else:
        author.save()
    print(f'Рейтинг автора уменьшился на {step_down}')


# Функция уменьшает рейтинг автора после одобрения жалобы по посту автора.
def author_rate_low_before_complain(author, min_rate=MIN_RATING_AUTHOR, step_down=STEP_DOWN_RATE_BEFORE_COMPLAIN):
    author.author_rating -= step_down
    author.author_rating = round(author.author_rating, 2)
    if author.author_rating < min_rate:
        author.author_rating = min_rate
        author.save()
    else:
        author.save()
    print(f'Рейтинг автора уменьшился на {step_down}')


# Функция уменьшает рейтинг автора после бана пользователя.
def author_rate_low_before_ban(author, min_rate=MIN_RATING_AUTHOR, step_down=STEP_DOWN_RATE_BEFORE_BAN):
    author.author_rating -= step_down
    author.author_rating = round(author.author_rating, 2)
    if author.author_rating < min_rate:
        author.author_rating = min_rate
        author.save()
    else:
        author.save()
    print(f'Рейтинг автора уменьшился на {step_down}')
