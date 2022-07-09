import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Group, Post
from .utils import check_post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # создаем запись в БД
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
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
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )
        cls.form = PostForm
        cls.POST_CREATE = '/create/'
        cls.PROFILE = f'/profile/{cls.user.username}/'
        cls.POST_EDIT = f'/posts/{cls.post.id}/edit/'
        cls.POST_DETAIL = f'/posts/{cls.post.id}/'

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)

    def test_post_edit(self):
        """Проверка создания формой редактированной записи в БД"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст из формы',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            self.POST_EDIT,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, self.POST_DETAIL
        )
        self.assertEqual(Post.objects.count(), post_count)
        post = Post.objects.first()
        check_post(post, self.post, **form_data)

    def test_post_create(self):
        """Проверка создания формой новой записи в БД."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст из формы',
            'group': self.group.id,
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            self.POST_CREATE,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, self.PROFILE
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        post = Post.objects.filter(text=form_data['text']).latest('text')
        check_post(post, self.post, **form_data)
        self.assertEqual(
            post.image, f"posts/{form_data['image'].name}"
        )

    def test_post_detail(self):
        """ Создание комментария на странице post_detail."""
        comment_count = Comment.objects.count()
        form_data = {
            'post': self.post,
            'text': 'Тестовый коммнетарий'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.POST_DETAIL)
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertEqual(
            Comment.objects.filter(text=form_data['text']).get().text,
            form_data['text']
        )
