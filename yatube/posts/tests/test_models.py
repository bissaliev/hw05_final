from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа_2',
            slug='Тестовый слаг_2',
            description='Тестовое описание_2',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовая пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        groups = Group.objects.all()
        for group in groups:
            with self.subTest(group=group):
                self.assertEqual(group.title, str(group))
        self.assertEqual(self.post.text, str(self.post))
