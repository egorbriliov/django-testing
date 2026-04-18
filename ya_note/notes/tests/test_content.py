from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note-slug',
            author=cls.author,
        )

    def test_notes_list_for_different_users(self):
        """
        Проверка, чтобы в список заметок одного пользователя не попадали,
        заметки другого c проверкой нахождения заметки внутри.
        """
        users = (
            (self.author, True),
            (self.reader, False),
        )
        url = reverse('notes:list')
        for user, value in users:
            self.client.force_login(user)
            with self.subTest(user=user):
                response = self.client.get(url)
                object_list = response.context['object_list']
                self.assertTrue((self.note in object_list) == value)

    def test_pages_contains_form(self):
        """
        Проверка содержания формы на страницах, для авторизированного
        пользователя.
        """
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        self.client.force_login(self.note.author)
        for page, args in urls:
            with self.subTest(page=page):
                url = reverse(page, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
