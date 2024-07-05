from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username="author")
        cls.user = User.objects.create_user(username="HasNoName")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text="Тестовая пост",
        )
        cls.comment = Comment.objects.create(
            post=cls.post, author=cls.user, text="Тестовый комментарий"
        )
        cls.name_templates = (
            ("posts:index", "posts/index.html", None),
            ("posts:group_list", "posts/index.html", [cls.group.slug]),
            ("posts:profile", "posts/profile.html", [cls.author.username]),
            ("posts:post_detail", "posts/post_detail.html", [cls.post.id]),
            ("posts:post_edit", "posts/create_post.html", [cls.post.id]),
            ("posts:post_create", "posts/create_post.html", None),
        )
        cls.ADD_COMMENT = reverse("posts:add_comment", args=[cls.post.id])

    def setUp(self):
        self.guest_client = Client()
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_url_exists_at_desired_location_user(self):
        """Страницы доступны авторизированному пользователю."""
        for name, template, arg in self.name_templates:
            with self.subTest(template=template):
                reverse_name = reverse(name, args=arg)
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_at_desired_location_author(self):
        """Страницы доступны авторизированному автору."""
        for name, template, arg in self.name_templates:
            with self.subTest(template=template):
                reverse_name = reverse(name, args=arg)
                response = self.authorized_author.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_redirect_anonymous_on_login(self):
        """Страница по адресу /create/ и /posts/post_id/edit/ перенаправит анонимного
        пользователя на страницу логина.
        """
        for name, template, arg in self.name_templates:
            with self.subTest(name=name):
                if template == "posts/create_post.html":
                    name_reverse = reverse(name, args=arg)
                    response = self.guest_client.get(name_reverse, follow=True)
                    self.assertRedirects(response, f"/auth/login/?next={name_reverse}")

    def test_url_unexists_at_desired_location(self):
        """Проверка запроса к несуществующей странице."""
        response = self.guest_client.get("/unexisting_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_page404(self):
        """Проверка редиректа на кастомный шаблон 404."""
        response = self.guest_client.get("/unexisting_page/")
        self.assertTemplateUsed(response, "core/404.html")

    def test_urls_uses_correct_template(self):
        """URL-адреса приложения posts  используют соответствующий шаблон."""
        for name, template, arg in self.name_templates:
            with self.subTest(template=template):
                response = self.authorized_author.get(reverse(name, args=arg))
                self.assertTemplateUsed(response, template)

    def test_add_comment_redirect_authorized(self):
        """
        При создании комментария авторизированного
        пользователя перенаправит на post_detail.
        """
        response = self.authorized_author.post(self.ADD_COMMENT)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, f"/posts/{self.post.id}/")

    def test_add_comment_redirect_unauthorized(self):
        """
        Неавторизированного пользователя перенаправит
        на страницу login.
        """
        response = self.guest_client.get(self.ADD_COMMENT)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, f"/auth/login/?next={self.ADD_COMMENT}")
