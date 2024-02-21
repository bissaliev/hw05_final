import datetime

from django.contrib.auth.forms import UserCreationForm
from django import forms

from django.contrib.auth import get_user_model


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
            'first_name',
            'last_name',
            'username',
            'email',
            'birth_date',
            'avatar'
        )
