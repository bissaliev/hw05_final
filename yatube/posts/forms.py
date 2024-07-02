from django import forms

from .models import Comment, Follow, Post


class PostForm(forms.ModelForm):
    """Класс-форма модели Post."""

    class Meta:
        model = Post
        fields = ("title", "text", "group", "image")


class CommentForm(forms.ModelForm):
    """Класс-форма модели Comment."""

    class Meta:
        model = Comment
        fields = ("text",)
        help_text = {"text": "Добавьте свой комменттарий"}
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Напишите свой комментарий",
                }
            )
        }


class FollowForm(forms.ModelForm):
    """
    Класс-форма для подписки и отписки на автора поста.
    """

    class Meta:
        model = Follow
        fields = ("author",)
        widgets = {
            "author": forms.HiddenInput(),
        }
