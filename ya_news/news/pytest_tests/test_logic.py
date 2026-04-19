from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client,
                                            news,
                                            comment_form_data):
    """Проверяет, чтобы анонимный пользователь не мог оставлять комментарии."""
    url = reverse('news:detail', args=(news.pk,))
    client.post(url, data=comment_form_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_auth_user_can_create_comment(
    author_client, news, comment_form_data
):
    """Проверяет, чтобы пользователь мог оставлять комментарии."""
    url = reverse('news:detail', args=(news.pk,))
    author_client.post(url, data=comment_form_data)
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_ban_words_error(
    author_client, news, comment_form_data
):
    """
    Проверяет, чтобы пользователь не мог отправлять комментарии с плохими
    словами.
    """
    url = reverse('news:detail', args=(news.pk,))
    comment_form_data['text'] = BAD_WORDS[0]
    response = author_client.post(url, data=comment_form_data)
    assertFormError(response.context['form'], 'text', errors=(WARNING))
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_edit_comment(
    author_client, comment, news, comment_form_data
):
    """Проверяет, чтобы автор мог редактировать свои комментарии."""
    url = reverse('news:edit', args=(comment.pk,))
    response = author_client.post(url, comment_form_data)
    expected_url = reverse('news:detail', args=(news.pk,)) + '#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == comment_form_data['text']


@pytest.mark.django_db
def test_other_user_cant_delete_comment(reader_client, comment):
    """Проверяет, чтобы читатель не мог удалять чужие комментарии."""
    url = reverse('news:delete', args=(comment.pk,))
    response = reader_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_other_user_cant_edit_comment(
    reader_client, comment, comment_form_data
):
    """Проверяет, чтобы читатель не мог редактировать чужие комментарии."""
    url = reverse('news:edit', args=(comment.pk,))
    response = reader_client.post(url, comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != comment_form_data['text']
