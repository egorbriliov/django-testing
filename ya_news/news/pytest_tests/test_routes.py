from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from django.urls import reverse


@pytest.mark.parametrize(
    'page, args',
    (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', pytest.lazy_fixture('news_pk'))  # type: ignore
    ),
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, page, args):
    """Проверка доступности страниц для ананомного пользователя."""
    url = reverse(page, args=args)
    response = client.post(url) if page == 'users:logout' else client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('page', ('news:edit', 'news:delete'))
@pytest.mark.django_db
def test_comment_interaction_availability_for_different_users(
    page, comment_pk, reader_client
):
    """Проверка изменния комментария пользовтелем не являющимся автором."""
    url = reverse(page, args=comment_pk)
    response = reader_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('page', ('news:edit', 'news:delete'))
@pytest.mark.django_db
def test_pages_availability_for_auth_user(
    page, comment_pk, author_client
):
    """Проверка изменния комментария пользовтелем являющимся автором."""
    url = reverse(page, args=comment_pk)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('page', ('news:edit', 'news:delete'))
@pytest.mark.django_db
def test_redicts(client, page, comment_pk):
    """Проверка перенаправлений анонимного пользоваеля."""
    login_url = reverse('users:login')
    url = reverse(page, args=comment_pk)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
