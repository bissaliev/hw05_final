from io import BytesIO

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image

from ..models import Comment, Follow, Group, Post
from .utils import check_post

User = get_user_model()


class TestPostCreation(TestCase):
    """Тестирование создание постов."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username="Author")
        cls.reader = User.objects.create(username="Reader")
        cls.group = Group.objects.create(
            title="group_1", slug="slug_group_1", description="Description for group_1"
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.anonymous_user = Client()
        cls.form_data = {
            "title": "Test create post",
            "text": "Testing create post",
            "group": cls.group.id,
        }
        cls.post_create_url = reverse("posts:post_create")

    def generate_image_file(self):
        file = BytesIO()
        image = Image.new("RGB", (100, 100))
        image.save(file, "jpeg")
        file.name = "test.jpg"
        file.seek(0)
        return file

    def test_anonymous_user_cant_create_post(self):
        """Тестируем что анонимный пользователь не может создать пост."""
        self.anonymous_user.post(self.post_create_url, data=self.form_data)
        posts_count = Post.objects.count()
        self.assertEqual(
            posts_count, 0, "\nАнонимный пользователь не может создавать посты."
        )

    def test_user_can_create_post(self):
        """Тестируем что авторизованный пользователь может создавать посты."""
        self.reader_client.post(self.post_create_url, data=self.form_data)
        posts_count = Post.objects.count()
        self.assertEqual(
            posts_count, 1, "\nАвторизованный пользователь может создавать посты."
        )


class TestPostEditDelete(TestCase):
    """Тестирование удаление и редактирование постов."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username="Author")
        cls.reader = User.objects.create(username="Reader")
        cls.group = Group.objects.create(
            title="group_1", slug="slug_group_1", description="Description for group_1"
        )
        cls.group_2 = Group.objects.create(
            title="group_2", slug="slug_group_2", description="Description for group_2"
        )
        cls.post_data = {"title": "Test title", "text": "Testing", "group": cls.group}
        cls.post = Post.objects.create(**cls.post_data, author=cls.author)
        cls.form_data = {
            "title": "Test edit post",
            "text": "Testing edit post",
            "group": cls.group_2.id,
        }
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.anonymous_user = Client()
        cls.edit_url = reverse("posts:post_edit", args=[cls.post.id])
        cls.delete_url = reverse("posts:post_delete", args=[cls.post.id])
        cls.post_detail_url = reverse("posts:post_detail", args=[cls.post.id])
        cls.index_url = reverse("posts:index")

    def test_author_can_delete_post(self):
        """Тестируем удаление поста автором."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.index_url)
        posts_count = Post.objects.count()
        self.assertEqual(posts_count, 0, "\nАвтор может удалить свой пост.")

    def test_user_cant_delete_post_of_another_user(self):
        """Тестируем удаление поста другим пользователем."""
        response = self.reader_client.delete(self.delete_url)
        self.assertRedirects(response, self.post_detail_url)
        posts_count = Post.objects.count()
        self.assertEqual(
            posts_count, 1, "\nДругой пользователь не может удалить чужой пост"
        )

    def test_author_can_edit_post(self):
        """Тестируем редактирование поста автором."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.post.refresh_from_db()
        self.assertRedirects(response, self.post.get_absolute_url())
        check_post(self.post, **self.form_data)

    def test_user_cant_edit_comment_of_another_user(self):
        """Тестируем редактирование поста другим пользователем."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.post.get_absolute_url())
        self.post.refresh_from_db()
        check_post(self.post, **self.post_data)


class TestCommentCreation(TestCase):
    """Тестирование создания комментариев."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username="Author")
        cls.reader = User.objects.create(username="Reader")
        cls.post = Post.objects.create(
            author=cls.author, title="Test title", text="Testing"
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.anonymous_user = Client()
        cls.form_data = {"text": "Test comment"}
        cls.url_comment_create = reverse("posts:post_detail", args=[cls.post.id])
        cls.url_login = reverse("users:login")

    def test_anonymous_user_cant_create_comment(self):
        """Тестирование создания комментария анонимным пользователем."""
        response = self.anonymous_user.post(
            self.url_comment_create, data=self.form_data
        )
        self.assertRedirects(
            response,
            f"{self.url_login}?next=/posts/{self.post.id}/",
        )
        comments_count = Comment.objects.count()
        self.assertEqual(
            comments_count,
            0,
            "\nКомментарий был создан анонимным пользователем.",
        )

    def test_user_can_create_comment(self):
        """Тестирование создания комментария авторизованным пользователем."""
        response = self.author_client.post(self.url_comment_create, data=self.form_data)
        self.assertRedirects(response, self.url_comment_create)
        comments_count = Comment.objects.count()
        self.assertEqual(
            comments_count,
            1,
            "\nКомментарий не был создан авторизованным пользователем.",
        )
        comment = Comment.objects.get()
        self.assertEqual(
            comment.author,
            self.author,
            "\nПоле `author` не соответствует ожидаемому результату.",
        )
        self.assertEqual(
            comment.text,
            self.form_data.get("text"),
            "\nПоле `text` не соответствует ожидаемому результату.",
        )


class TestCommentEditDelete(TestCase):
    """Тестирование редактирования и создания комментариев."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username="Author")
        cls.reader = User.objects.create(username="Reader")
        cls.post = Post.objects.create(
            author=cls.author, title="Test title", text="Testing"
        )
        cls.comment = Comment.objects.create(
            post=cls.post, author=cls.author, text="First comment"
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.anonymous_user = Client()
        cls.form_data = {"text": "Second comment"}
        cls.url_post_detail = reverse("posts:post_detail", args=[cls.post.id])
        cls.url_comment_delete = reverse("posts:comment_delete", args=[cls.comment.id])
        cls.url_comment_edit = reverse("posts:comment_edit", args=[cls.comment.id])

    def test_author_can_delete_comment(self):
        """Тестирование удаления комментария его автором."""
        response = self.author_client.delete(self.url_comment_delete)
        self.assertRedirects(response, self.url_post_detail + "#comments")
        comments_count = Comment.objects.count()
        self.assertEqual(
            comments_count, 0, "\nПользователь может удалить свой комментарий."
        )

    def test_user_cant_delete_comment_of_another_user(self):
        """Тестирование удаления чужого комментария пользователем."""
        response = self.reader_client.delete(self.url_comment_delete)
        self.assertRedirects(response, self.url_post_detail)
        comments_count = Comment.objects.count()
        self.assertEqual(
            comments_count, 1, "\nПользователь не может удалить чужой комментарий."
        )

    def test_author_can_edit_post(self):
        """Тестирование редактирования комментария его автором."""
        response = self.author_client.post(self.url_comment_edit, data=self.form_data)
        self.assertRedirects(response, self.url_post_detail + "#comments")
        self.comment.refresh_from_db()
        self.assertEqual(
            self.comment.text,
            self.form_data.get("text"),
            "\nПользователь может редактировать свой комментарий.",
        )

    def test_user_cant_edit_comment_of_another_user(self):
        """Тестирование редактирования чужого комментария пользователем."""
        response = self.reader_client.post(self.url_comment_edit, data=self.form_data)
        self.assertRedirects(response, self.url_post_detail)
        self.comment.refresh_from_db()
        self.assertNotEqual(
            self.comment.text,
            self.form_data.get("text"),
            "\nПользователь не может редактировать чужой комментарий.",
        )


class TestFollow(TestCase):
    """Тестирование подписок."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username="Author")
        cls.reader = User.objects.create(username="Reader")
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.anonymous_user = Client()
        cls.url_follow = reverse("posts:profile_follow")
        cls.form_data = {"author": cls.author.id}

    def test_user_can_subscribe_to_author(self):
        """Тестирование подписки авторизованного пользователя на автора."""
        response = self.reader_client.post(self.url_follow, data=self.form_data)
        self.assertRedirects(response, "/")
        followers_count = Follow.objects.count()
        self.assertEqual(
            followers_count,
            1,
            "\nАвторизованный пользователь может подписаться на автора.",
        )

    def test_anonymous_user_cant_subscribe_to_author(self):
        """Тестирование подписки анонимного пользователя на автора."""
        self.anonymous_user.post(self.url_follow, data=self.form_data)
        followers_count = Follow.objects.count()
        self.assertEqual(
            followers_count,
            0,
            "\nАнонимный пользователь не может подписаться на автора.",
        )

    def test_author_cant_subscribe_to_author(self):
        """Тестирование подписки автора на самого себя."""
        self.author_client.post(self.url_follow, data=self.form_data)
        followers_count = Follow.objects.count()
        self.assertEqual(
            followers_count, 0, "\nАвтор не может подписаться на самого себя."
        )

    def test_user_can_unsubscribe_from_author(self):
        """Тестирование отписки пользователя от автора."""
        Follow.objects.create(author=self.author, user=self.reader)
        followers_count_before = Follow.objects.count()
        self.reader_client.post(self.url_follow, data=self.form_data)
        followers_count_after = Follow.objects.count()
        self.assertEqual(
            followers_count_before,
            followers_count_after + 1,
            "\nПользователь может отписаться от автора.",
        )
