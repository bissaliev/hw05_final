from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post

User = get_user_model()


class TestPostRoutes(TestCase):
    """Тестирование маршрутов постов."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username="Author")
        cls.reader = User.objects.create(username="Reader")
        cls.group = Group.objects.create(
            title="group_1",
            slug="slug_group_1",
            description="Description for group_1",
        )
        cls.post = Post.objects.create(
            title="Test title", text="Testing", author=cls.author
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.anonymous_user = Client()

    def test_pages_availability_for_anonymous_client(self):
        """
        Тестирование маршрутов доступные любому неавторизованному пользователю.
        """
        urls = (
            ("posts:index", None),
            ("posts:post_detail", (self.post.id,)),
            ("posts:post_of_group", (self.group.slug,)),
            ("posts:search", None),
        )
        for item in urls:
            name, args = item
            with self.subTest(name=name):
                response = self.anonymous_user.get(reverse(name, args=args))
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    "\nОжидаемый статус ответа для анонимного пользователя 200.",
                )

    def test_pages_availability_for_user(self):
        """
        Тестирование маршрутов доступные любому авторизованному пользователю.
        """
        urls = (
            ("users:profile", [self.author.username]),
            ("posts:follow_index", None),
            ("posts:post_create", None),
        )
        for item in urls:
            name, args = item
            with self.subTest(name=name):
                response = self.reader_client.get(reverse(name, args=args))
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    "\nОжидаемый статус ответа для авторизованного пользователя 200.",
                )

    def test_pages_availability_edit_delete(self):
        """Тестирование маршрутов редактирования и удаления постов."""

        users_status = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.FOUND),
        )
        for user, status in users_status:
            for url in ("posts:post_delete", "posts:post_edit"):
                with self.subTest(user=user, url=url):
                    response = user.get(reverse(url, args=[self.post.id]))
                    self.assertEqual(
                        response.status_code,
                        status,
                        "\nРедактирование и удаление постов доступны только автору.",
                    )

    def test_redirect_for_anonymous_client(self):
        """
        Тестирование перенаправления анонимного пользователя на страницу входа.
        """
        login_url = reverse("users:login")
        names = (
            ("posts:post_delete", [self.post.id]),
            ("posts:post_edit", [self.post.id]),
            ("posts:follow_index", None),
            ("users:profile", [self.author.username]),
        )
        for name, args in names:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f"{login_url}?next={url}"
                response = self.anonymous_user.get(url, follow=True)
                self.assertRedirects(response, redirect_url)


class TestCommentRoutes(TestCase):
    """Тестирование маршрутов комментариев."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username="Author")
        cls.reader = User.objects.create(username="Reader")
        cls.post = Post.objects.create(
            title="Test title", text="Testing", author=cls.author
        )
        cls.comment = Comment.objects.create(
            author=cls.author, post=cls.post, text="Test comment"
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

    def test_comments_url_for_edit_delete_is_available_to_user(self):
        """Тестирование маршрутов редактирования и удаления комментариев."""
        users_status = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.FOUND),
        )
        for user, status in users_status:
            for name in ("posts:comment_edit", "posts:comment_delete"):
                with self.subTest(user=user, name=name):
                    response = user.get(reverse(name, args=[self.comment.id]))
        self.assertEqual(
            response.status_code,
            status,
            "\nРедактирование и удаление комментариев доступны только автору.",
        )
