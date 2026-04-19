from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Тестовый текст',
            slug='test',
            author=cls.author
        )

    def test_pages_availability(self):
        """Проверка доступности страниц для неаундифицированного
        пользователя.
        """
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        """
        Тест перенаправления анонимного пользователя на страницу логина. При
        попытке его перехода на:
        1. Список заметок
        2. Страницу успешного добавления записи
        3. Страницу добавления заметки
        4. Страницу отдельной заметки
        5. Страницу редактирования заметки
        6. Страницу удаления заметки
        """
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug, )),
            ('notes:edit', (self.note.slug, )),
            ('notes:delete', (self.note.slug, )),
        )
        login_url = reverse('users:login')
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_auth_user_pages_availability(self):
        """
        Проверка доступности авторизированному пользователю страниц:
        1. Cо списком заметок notes/,
        2. Cтраница успешного добавления заметки done/
        3. Cтраница добавления новой заметки add/.
        """
        self.client.force_login(self.reader)
        for name in ('notes:list', 'notes:success', 'notes:add'):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        """Проверка авторизации пользователя."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
