import datetime

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    """Регистрация нового пользователя."""

    this_year = datetime.date.today().year
    birth_date = forms.DateField(
        widget=forms.SelectDateWidget(
            years=tuple(range(this_year - 100, this_year - 10))
        )
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
    this_year = datetime.date.today().year
    # birth_date = forms.DateField(
    # label="Дата рождения",
    # widget=forms.SelectDateWidget(
    # years=tuple(range(this_year - 100, this_year - 10))
    # ),
    # )
    birth_date = forms.DateField(
        label="Дата рождения",
        widget=forms.DateInput(
            attrs={
                "type": "date",
            }
        ),
    )

    class Meta:
        model = User
        fields = (
            "avatar",
            "first_name",
            "last_name",
            "username",
            "email",
            "birth_date",
        )
