from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class RoleModel(models.TextChoices):
        administrator = 'administrator'
        moderator = 'moderator'
        user = 'user'

    user_role = models.CharField(
        max_length=16,
        choices=RoleModel.choices,
        default=RoleModel.user,
    )

    class SexModel(models.TextChoices):
        male = 'Мужской'
        female = 'Женский'
        undefined = 'Не выбран'

    sex = models.CharField(
        max_length=10,
        choices=SexModel.choices,
        default=SexModel.undefined,
        verbose_name='Пол',
    )

    avatar = models.ImageField(verbose_name='Аватар',
                               upload_to='user_avatar',
                               blank=True,
                               null=True)

    about_me = models.TextField(verbose_name='Обо мне',
                                max_length=512,
                                blank=True)

    age = models.IntegerField(verbose_name='Возраст',
                              default=0)

    follows = models.ManyToManyField('self', related_name='follow', symmetrical=False)

    followers = models.ManyToManyField('self', related_name='follow_user', symmetrical=False)

    author_rating = models.FloatField(verbose_name="Рейтинг автора",
                                      default=4)

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.first_name.title()} {self.last_name.title()} ({self.username})'

    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.save()
