from http import HTTPStatus

from django.contrib.auth import get_user_model

from .conftest import BaseClass

User = get_user_model()


class TestRoutes(BaseClass):

    def test_pages_availability(self):
        """Проверка доступности страниц для неаундифицированного
        пользователя.
        """
        test_data = (
            # Неавтаризованный
            (self.HOME_URL, self.client, HTTPStatus.OK),
            (self.LOGIN_URL, self.client, HTTPStatus.OK),
            (self.SINGUP_URL, self.client, HTTPStatus.OK),
            # Авторизованный
            (self.NOTES_LIST_URL, self.reader_client, HTTPStatus.OK),
            (self.SUCCESS_NOTE_URL, self.reader_client, HTTPStatus.OK),
            (self.ADD_NOTE_URL, self.reader_client, HTTPStatus.OK),
            # Удаление и редактирвоание заметкм
            (self.DETAIL_NOTE_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.DELETE_NOTE_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.EDIT_NOTE_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.DETAIL_NOTE_URL, self.author_client, HTTPStatus.OK),
            (self.DELETE_NOTE_URL, self.author_client, HTTPStatus.OK),
            (self.EDIT_NOTE_URL, self.author_client, HTTPStatus.OK),
        )
        for url, client, status in test_data:
            with self.subTest(client=client, url=url, status=status):
                response = client.get(url)
                self.assertEqual(response.status_code, status)

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
            self.NOTES_LIST_URL,
            self.SUCCESS_NOTE_URL,
            self.ADD_NOTE_URL,
            self.EDIT_NOTE_URL,
            self.DELETE_NOTE_URL,
            self.DETAIL_NOTE_URL
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{self.LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
