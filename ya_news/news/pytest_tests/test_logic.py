from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_anonim_user_cant_create_comment(anonim_client, comment, detail_url):
    """Проверяет, чтобы анонимный пользователь не мог оставлять комментарии."""
    before_comment_count = Comment.objects.count()
    anonim_client.post(detail_url, data={'text': comment.text})
    after_comment_count = Comment.objects.count()
    assert before_comment_count == after_comment_count


def test_auth_user_can_create_comment(author_client, comment, detail_url):
    """Проверяет, чтобы пользователь мог оставлять комментарии."""
    before_comment_count = Comment.objects.count()
    author_client.post(detail_url, data={'text': comment.text})
    after_comment_count = Comment.objects.count()
    assert after_comment_count == before_comment_count + 1


@pytest.mark.parametrize('ban_word', BAD_WORDS)
def test_ban_words_error(author_client, ban_word, edit_url):
    """
    Проверяет, чтобы пользователь не мог отправлять комментарии с плохими
    словами.
    """
    before_comment_count = Comment.objects.count()
    response = author_client.post(edit_url, data={'text': ban_word})
    after_comment_count = Comment.objects.count()
    assertFormError(response.context['form'], 'text', errors=(WARNING))
    assert after_comment_count == before_comment_count


def test_author_can_edit_comment(author_client, comment, detail_url, edit_url):
    """Проверяет, чтобы автор мог редактировать свои комментарии."""
    form_data = {'text': 'new_text'}
    response = author_client.post(edit_url, data=form_data)
    expected_url = detail_url + '#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_other_user_can_delete_comment(author_client, delete_url, comment):
    """Проверяет, чтобы втор мог удалять свои комментарии."""
    response = author_client.post(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_other_user_cant_delete_comment(reader_client, delete_url, comment):
    """Проверяет, чтобы читатель не мог удалять чужие комментарии."""
    response = reader_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment.pk).exists()


def test_other_user_cant_edit_comment(reader_client, comment, edit_url):
    """Проверяет, чтобы читатель не мог редактировать чужие комментарии."""
    form_data = {'text': 'new_text'}
    response = reader_client.post(edit_url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text != form_data['text']
