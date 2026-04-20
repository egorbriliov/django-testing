from django.contrib.auth import get_user_model

from notes.forms import NoteForm

from .conftest import BaseClass

User = get_user_model()


class TestContent(BaseClass):
    # @unittest.skip('Failure')
    def test_notes_list_for_different_users(self):
        """
        Проверка, чтобы в список заметок одного пользователя не попадали,
        заметки другого c проверкой нахождения заметки внутри.
        """
        users = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        for client, value in users:
            with self.subTest(client=client):
                response = client.get(self.NOTES_LIST_URL)
                object_list = response.context['object_list']
                self.assertTrue((self.note in object_list) == value)

    def test_pages_contains_form(self):
        """
        Проверка содержания формы на страницах, для авторизированного
        пользователя.
        """
        for url in (self.ADD_NOTE_URL, self.EDIT_NOTE_URL):
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIsInstance(response.context.get('form'), NoteForm)
