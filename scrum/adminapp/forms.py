from django.contrib.auth.forms import UserCreationForm
from django.forms import TextInput, EmailInput

from authapp.models import User


class AdminUserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username', 'password1', 'password2', 'email', 'first_name',
            'last_name', 'user_role'
        )

        widgets = {
            'username': TextInput(attrs={'placeholder': 'user123'}),
            'email': EmailInput(attrs={'placeholder': 'example@domain.com'}),
            'first_name': TextInput(attrs={'placeholder': 'Иван'}),
            'last_name': TextInput(attrs={'placeholder': 'Иванов'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Имя пользователя"
        self.fields['password1'].label = "Пароль"
        self.fields['password2'].label = "Введите пароль еще раз"
        self.fields['email'].label = "Почтовый адрес"
        self.fields['first_name'].label = "Имя"
        self.fields['last_name'].label = "Фамилия"
        self.fields['user_role'].label = "Роль"
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = f'form-control {field_name}'
            field.help_text = ''

