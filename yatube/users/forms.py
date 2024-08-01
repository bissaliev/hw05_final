from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

User = get_user_model()


class RegisterForm(UserCreationForm):
    """Регистрация нового пользователя."""

    email = forms.EmailField(required=True, label="Адрес электронной почты")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
        )


class ProfileEditForm(UserChangeForm):
    birth_date = forms.DateField(
        label="Дата рождения",
        widget=forms.DateInput(
            attrs={
                "type": "date",
            }
        ),
    )
    email = forms.EmailField(required=True, label="Адрес электронной почты")

    class Meta(UserChangeForm.Meta):
        model = User
        fields = (
            "avatar",
            "first_name",
            "last_name",
            "username",
            "email",
            "birth_date",
        )
