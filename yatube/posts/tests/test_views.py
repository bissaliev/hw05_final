import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='HasNoName')
        cls.user = User.objects.create_user(username='User')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_not = Group.objects.create(
            title='Тестовая группа_2',
            slug='test-slug_2',
            description='Тестовое описание_2'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author,
            text='Тестовый комментарий'
        )
        cls.name_templates = (
            ('posts:index', 'posts/index.html', None),
            ('posts:group_list', 'posts/group_list.html', [cls.group.slug]),
            ('posts:profile', 'posts/profile.html', [cls.author.username]),
            ('posts:post_detail', 'posts/post_detail.html', [cls.post.id]),
            ('posts:post_edit', 'posts/create_post.html', [cls.post.id]),
            ('posts:post_create', 'posts/create_post.html', None),
        )
        cls.index = '/'
        cls.follow_index = '/follow/'
        cls.profile_follow = f'/profile/{cls.post.author}/follow/'
        cls.profile_unfollow = f'/profile/{cls.post.author}/unfollow/'
        cls.post_edit = f'/posts/{cls.post.id}/edit/'
        cls.post_detail = f'/posts/{cls.post.id}/'

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post.author)
        self.guest_client = Client()
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for name, template, arg in self.name_templates:
            with self.subTest(template=template):
                reverse_name = reverse(name, args=arg)
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_page_show_correct_context(self):
        """Шаблон index, group_list, profile
        сформированы с правильным контекстом.
        """
        COUNT_POST_NULL = 0
        names = ('posts:index', 'posts:group_list', 'posts:profile')
        for name, template, arg in self.name_templates:
            if name is names:
                with self.subTest(template=template):
                    response = self.authorized_author.get(
                        reverse(name, args=arg)
                    )
                    first_object = (
                        response.context['page_obj'][COUNT_POST_NULL]
                    )
                    self.assertEqual(first_object.text, self.post.text)
                    self.assertEqual(
                        first_object.author.username, self.post.author.username
                    )
                    self.assertEqual(
                        first_object.group.title, self.group.title
                    )
                    self.assertEqual(
                        first_object.group.description,
                        self.group.description
                    )
                    self.assertNotEqual(
                        first_object.group.title, self.group_not.title
                    )
                    self.assertEqual(
                        first_object.image, f'posts/{self.uploaded.name}'
                    )

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            self.post_detail
        )
        post = response.context['post']
        comments = response.context['comments']
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(
            post.author.username, self.post.author.username
        )
        self.assertEqual(post.image, f'posts/{self.uploaded.name}')
        self.assertEqual(response.context['count_author'], 1)
        comment_fields = (
            (comments.get().text, self.comment.text),
            (comments.get().author, self.comment.author),
            (comments.get().post, self.comment.post),
            (comments.get().id, self.comment.id)
        )
        for field, expected in comment_fields:
            with self.subTest(field=field):
                self.assertEqual(field, expected)
        self.assertIsInstance(
            response.context.get('form').fields.get('text'),
            forms.fields.CharField
        )

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            self.post_edit
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                self.assertIsInstance(
                    response.context.get('form').fields.get(value), expected
                )

    def test_cache_index_page(self):
        """Тестирование работы кеширования на главной странице."""
        post = Post.objects.create(
            author=self.author,
            text='Тестируем кеш'
        )

        cache.clear()
        content_index = self.authorized_author.get(
            self.index
        ).content
        Post.objects.filter(author=post.author, text=post.text).delete()
        self.assertEqual(
            self.authorized_author.get(self.index).content,
            content_index
        )
        cache.clear()
        self.assertNotEqual(
            self.authorized_author.get(self.index).content,
            content_index
        )

    def test_follow_authorized_user(self):
        """
        Проверка подписки авторизированным
        пользователем на других пользователей и
        только один раз.
        """
        count_follow = self.user.follower.count()
        self.authorized_user.post(
            self.profile_follow
        )
        count_follow_2 = self.user.follower.count()
        self.authorized_user.post(
            self.profile_follow
        )
        self.assertEqual(count_follow_2, count_follow + 1)
        self.assertEqual(self.user.follower.count(), count_follow + 1)

    def test_unfollow(self):
        """Проверка отписки от автора."""
        self.authorized_user.post(
            self.profile_follow
        )
        count_follow = self.user.follower.count()
        self.authorized_user.post(
            self.profile_unfollow
        )
        self.assertEqual(self.user.follower.count(), count_follow - 1)

    def test_follow_index_count(self):
        """
        Проверка ленты постов подписанных
        и неподписанных ползователей.
        """
        author = self.post.author
        text = 'Пост для проверки подписок'
        authorized_user_2 = Client()
        authorized_user_2.force_login(
            User.objects.create_user(username='User_2')
        )
        self.authorized_user.post(
            self.profile_follow
        )
        count_user = len(self.authorized_user.get(
            self.follow_index
        ).context['page_obj'])
        count_user_2 = len(authorized_user_2.get(
            self.follow_index
        ).context['page_obj'])
        Post.objects.create(author=author, text=text)
        self.assertEqual(len(self.authorized_user.get(
            self.follow_index
        ).context['page_obj']), count_user + 1)
        self.assertEqual(len(authorized_user_2.get(
            self.follow_index
        ).context['page_obj']), count_user_2)


class PaginatorViewsTest(TestCase):
    """ Проверка паджинатора."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем 13 записей в БД
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for i in range(1, 14):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {str(i)}',
                group=cls.group
            )
        cls.index = '/'

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)
        cache.clear()

    def test_page_contains_records(self):
        """
        Проверка паджинатора: количество постов
        на первой и второй страницах равно соответственно 10 и 3.
        """
        POST_LIMIT = 10
        POST_LIMIT_2 = 3
        response = self.authorized_client.get(self.index)
        self.assertEqual(len(response.context['page_obj']), POST_LIMIT)
        response = self.authorized_client.get(
            self.index + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), POST_LIMIT_2)
