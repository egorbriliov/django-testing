from http import HTTPStatus

import pytest
from django.urls import reverse
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertFormError, assertRedirects


def test_anonymous_user_cant_create_comment(anonim_client, news, comment):
    """Проверяет, чтобы анонимный пользователь не мог оставлять комментарии."""
    url = reverse('news:detail', args=(news.pk,))
    before_comment_count = Comment.objects.count()
    anonim_client.post(url, data={'text': comment.text})
    after_comment_count = Comment.objects.count()
    assert before_comment_count == after_comment_count


def test_auth_user_can_create_comment(author_client, comment, detail_url):
    """Проверяет, чтобы пользователь мог оставлять комментарии."""
    before_comment_count = Comment.objects.count()
    author_client.post(detail_url, data={'text': comment.text})
    after_comment_count = Comment.objects.count()
    assert after_comment_count != before_comment_count


@pytest.mark.parametrize('ban_word', (word for word in BAD_WORDS))
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
    response = author_client.post(edit_url, {'text': 'test'})
    expected_url = detail_url + '#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == 'test'


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
    response = reader_client.post(edit_url, {'text': 'test'})
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != 'test'
