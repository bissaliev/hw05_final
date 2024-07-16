import datetime

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    """Регистрация нового пользователя."""

    birth_date = forms.DateField(
        label="Дата рождения",
        widget=forms.DateInput(
            attrs={
                "type": "date",
            }
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "birth_date",
            "avatar",
        )


class ProfileForm(UserChangeForm):
    birth_date = forms.DateField(
        label="Дата рождения",
        widget=forms.DateInput(
            attrs={
                "type": "date",
            }
        ),
    )

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
