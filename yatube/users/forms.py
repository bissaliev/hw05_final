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

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Электронная почта уже используется.")
        return email


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

    def clean_email(self):
        email = self.cleaned_data["email"]
        qs = User.objects.exclude(id=self.instance.id).filter(email=email)
        if qs.exists():
            raise forms.ValidationError("Электронная почта уже используется.")
        return email
