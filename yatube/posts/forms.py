from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """ Класс-форма модели Post."""
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    """ Класс-форма модели Comment."""
    class Meta:
        model = Comment
        fields = ('text',)
        help_text = {'text': 'Добавьте свой комменттарий'}
