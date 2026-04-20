from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

from .conftest import BaseClass

User = get_user_model()


class TestNoteCreation(BaseClass):
    """Тестирует создание заметки."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {'title': 'Form title',
                         'text': 'Form text',
                         'slug': 'form-slug'}

    def test_anonymous_user_cant_create_note(self):
        """Проверяет, чтобы анонимный пользовтель не мог создавать заметки."""
        before_notes_count = Note.objects.count()
        self.client.post(self.ADD_NOTE_URL, self.form_data)
        self.assertEqual(before_notes_count, Note.objects.count())

    def test_user_can_create_note(self):
        """Проверяет, чтобы залогинееный пользователь мог создавать заметки."""
        before_notes_count = Note.objects.count()
        response = self.author_client.post(self.ADD_NOTE_URL, self.form_data)
        self.assertRedirects(response, self.SUCCESS_NOTE_URL)
        self.assertNotEqual(before_notes_count, Note.objects.count())
        note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_empty_slug(self):
        """Проверяет автоматического заполнения slug заметки."""
        form_data = self.form_data.copy()
        del form_data['slug']
        before_notes_count = Note.objects.count()
        response = self.author_client.post(self.ADD_NOTE_URL, form_data)
        self.assertRedirects(response, self.SUCCESS_NOTE_URL)
        self.assertNotEqual(before_notes_count, Note.objects.count())
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(expected_slug, Note.objects.last().slug)

    def test_uniq_slug(self):
        """Проверяет уникальности slug заметки при создании."""
        self.author_client.post(self.ADD_NOTE_URL, self.form_data)
        response = self.author_client.post(self.ADD_NOTE_URL, self.form_data)
        self.assertFormError(
            form=response.context['form'],
            field='slug',
            errors=self.form_data['slug'] + WARNING,
        )  # type: ignore


class TestNoteEditDelete(BaseClass):
    """
    Тестирует изменение и удаление заметки собственной заметки и
    невозможность для чужой.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
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
        """Проверяет возможность удаления заметки для создателя."""
        before_notes_count = Note.objects.count()
        response = self.author_client.post(self.DELETE_NOTE_URL)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.SUCCESS_NOTE_URL)
        self.assertNotEqual(before_notes_count, Note.objects.count())

    def test_anonymous_user_cant_edit_note(self):
        """Проверяет возможность изменения заметки для анонима."""
        response = self.client.post(self.EDIT_NOTE_URL,
                                    data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        previous_data = {
            'title': self.note.title,
            'text': self.note.text
        }
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, previous_data['title'])
        self.assertEqual(self.note.text, previous_data['text'])

    def test_anonymous_user_cant_delete_note(self):
        """Проверяет возможность изменения заметки для анонима."""
        before_notes_count = Note.objects.count()
        response = self.reader_client.delete(self.DELETE_NOTE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(before_notes_count, Note.objects.count())
