from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify

User = get_user_model()


class TestNoteCreation(TestCase):
    """Тестирует создание заметки."""
    ADD_NOTE_URL = reverse('notes:add')
    SUCCESS_NOTE_URL = reverse('notes:success')

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)
        cls.form_data = {'title': 'Form title',
                         'text': 'Form text',
                         'slug': 'form-slug'}

    def test_anonymous_user_cant_create_note(self):
        """Проверяет, чтобы анонимный пользовтель не мог создавать заметки."""
        self.client.post(self.ADD_NOTE_URL, self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        """Проверяет, чтобы залогинееный пользовтель мог создавать заметки."""
        response = self.author_client.post(self.ADD_NOTE_URL, self.form_data)
        self.assertRedirects(response, self.SUCCESS_NOTE_URL)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.user)

    def test_empty_slug(self):
        """Проверяет автоматического заполнения slug заметки."""
        del self.form_data['slug']
        response = self.author_client.post(self.ADD_NOTE_URL, self.form_data)
        self.assertRedirects(response, self.SUCCESS_NOTE_URL)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        expected_slug = slugify(self.form_data['title'])
        note = Note.objects.get()
        self.assertEqual(expected_slug, note.slug)

    def test_uniq_slug(self):
        """Проверяет уникальности slug заметки при создании."""
        self.author_client.post(self.ADD_NOTE_URL, self.form_data)
        response = self.author_client.post(self.ADD_NOTE_URL, self.form_data)
        self.assertFormError(
            form=response.context['form'],
            field='slug',
            errors=self.form_data['slug'] + WARNING,
        )  # type: ignore


class TestNoteEditDelete(TestCase):
    """
    Тестирует изменение и удаление заметки собственной заметки и
    невозможность для чужой.
    """
    ADD_NOTE_URL = reverse('notes:add')
    SUCCESS_NOTE_URL = reverse('notes:success')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель простой')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='title',
            text='text',
            slug='slug',
            author=cls.author,
        )

        cls.EDIT_NOTE_URL = reverse('notes:edit', args=(cls.note.slug, ))
        cls.DELETE_NOTE_URL = reverse('notes:delete', args=(cls.note.slug, ))

        cls.form_data = {
            'title': 'new_title',
            'text': 'new_text'
        }

    def test_author_can_edit_note(self):
        """Проверяет возможность изменения заметки для создателя."""
        response = self.author_client.post(self.EDIT_NOTE_URL,
                                           data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_NOTE_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])

    def test_author_can_delete_note(self):
        """Проверяет возможность изменения заметки для создателя."""
        response = self.author_client.delete(self.DELETE_NOTE_URL)
        self.assertRedirects(response, self.SUCCESS_NOTE_URL)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), 0)

    def test_anonymous_user_cant_edit_note(self):
        """Проверяет возможность изменения заметки для анонима."""
        response = self.reader_client.post(self.EDIT_NOTE_URL,
                                           data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        previous_data = {
            'title': self.note.title,
            'text': self.note.text
        }
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, previous_data['title'])
        self.assertEqual(self.note.text, previous_data['text'])

    def test_anonymous_user_cant_delete_note(self):
        """Проверяет возможность изменения заметки для анонима."""
        response = self.reader_client.delete(self.DELETE_NOTE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
