import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from users.models import Follow

from ..models import Comment, Group, Post
from .utils import check_fields_of_post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=True
)
class TestPost(TestCase):
    TITLE_POST = "Post_"
    TEXT_POST = "Test text"

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username="Author")
        cls.reader = User.objects.create(username="Reader")
        cls.group = Group.objects.create(
            title="group_1",
            slug="slug_group_1",
            description="Description for group_1",
        )
        cls.small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xff\xff\xff\x21\xf9\x04\x00\x00"
            b"\x00\x00\x00\x2c\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0c"
            b"\x0a\x00\x3b"
        )
        cls.uploaded = SimpleUploadedFile(
            name="small.gif", content=cls.small_gif, content_type="image/gif"
        )
        now = timezone.now()
        for i in range(settings.PAGE_SIZE + 1):
            post = Post.objects.create(
                title=f"{cls.TITLE_POST}{i}",
                text=cls.TEXT_POST,
                author=cls.author,
                group=cls.group,
                image=cls.uploaded,
            )
            post.pub_date = now - timezone.timedelta(days=i)
            post.save()
        cls.posts = Post.objects.all()[: settings.PAGE_SIZE]
        cls.post = cls.posts[0]
        Follow.objects.create(author=cls.author, user=cls.reader)

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.reverse_names = (
            reverse("posts:index"),
            reverse("posts:post_of_group", args=[cls.group.slug]),
            reverse("users:profile", args=[cls.author.username]),
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_posts_count_on_index_page(self):
        """Проверка количества постов на странице."""
        for reverse_name in self.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.reader_client.get(reverse_name)
                posts = response.context.get("posts")
                posts_count = len(posts)
                self.assertEqual(
                    posts_count,
                    settings.PAGE_SIZE,
                    (
                        f"\nКоличество постов по адресу {reverse_name} "
                        f"должно быть {settings.PAGE_SIZE}"
                    ),
                )

    def test_posts_order_on_index_page(self):
        """Проверка сортировки постов."""
        for reverse_name in self.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.reader_client.get(reverse_name)
                posts = response.context.get("posts")
                all_dates = [post.pub_date for post in posts]
                sorted_dates = sorted(all_dates, reverse=True)
                self.assertEqual(
                    all_dates,
                    sorted_dates,
                    (
                        f"\nПосты по адресу {reverse_name} должны быть "
                        "отсортированы по дате публикации на убывание."
                    ),
                )

    def test_page_show_correct_context(self):
        """Проверка контекста."""
        for reverse_name in self.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.reader_client.get(reverse_name)
                posts = response.context.get("posts")
                for post_1, post_2 in zip(posts, self.posts):
                    check_fields_of_post(post_1, post_2)

    def test_post_detail_show_correct_context(self):
        """Проверка контекста на странице детальной информации о посте."""
        response = self.reader_client.get(
            reverse("posts:post_detail", args=[self.post.id])
        )
        post = response.context.get("post")
        check_fields_of_post(post, self.post)

    def test_post_create_show_correct_context(self):
        """Проверка что в контексте при создании поста передается форма."""
        post_create_url = reverse("posts:post_create")
        response = self.author_client.get(post_create_url)
        self.assertIn(
            "form",
            response.context,
            f"\nВ контексте по адресу {post_create_url} не обнаружена форма.",
        )

    def test_post_edit_show_correct_context(self):
        """
        Проверка что в контексте при редактировании поста передается форма.
        """
        post_edit_url = reverse("posts:post_edit", args=[self.post.id])
        response = self.author_client.get(post_edit_url)
        self.assertIn(
            "form",
            response.context,
            f"\nВ контексте по адресу {post_edit_url} не обнаружена форма.",
        )


class TestComment(TestCase):
    """Тестирование комментариев."""

    COMMENTS_COUNT = 5

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username="Author")
        cls.reader = User.objects.create(username="Reader")
        cls.post = Post.objects.create(
            title="test post", text="text for testing", author=cls.author
        )
        now = timezone.now()
        for index in range(cls.COMMENTS_COUNT):
            comment = Comment.objects.create(
                post=cls.post,
                author=cls.author,
                text=f"Testing comment_{index}",
            )
            comment.created = now - timezone.timedelta(days=index)
            comment.save()
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

    def test_comments_count(self):
        """
        Проверка количества комментариев к данному посту.
        """
        response = self.reader_client.get(
            reverse("posts:post_detail", args=[self.post.id])
        )
        comments = response.context.get("post").comments.all()
        self.assertEqual(
            len(comments),
            self.COMMENTS_COUNT,
            "\nКоличество комментариев не соответствует заданным параметрам.",
        )

    def test_comments_order(self):
        """
        Проверка на правильность сортировки комментариев.
        """
        response = self.reader_client.get(
            reverse("posts:post_detail", args=[self.post.id])
        )
        comments = response.context.get("post").comments.all()
        all_dates = [comment.created for comment in comments]
        sorted_dates = sorted(all_dates, reverse=True)
        self.assertEqual(
            all_dates,
            sorted_dates,
            "\nКомментарии на странице `post_detail.html` должны быть "
            "отсортированы по дате публикации на убывание.",
        )

    def test_authorized_client_has_form(self):
        """
        Проверка что в контексте детальной информации поста присутствует
        форма комментариев.
        """
        response = self.reader_client.get(
            reverse("posts:post_detail", args=[self.post.id])
        )
        self.assertIn(
            "form",
            response.context,
            "\nВ контексте страницы `post_detail.html` не обнаружена форма.",
        )
