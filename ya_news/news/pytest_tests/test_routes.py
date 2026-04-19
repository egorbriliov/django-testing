from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf


@pytest.mark.parametrize(
    'url, client_obj, expected_status',
    (
        # Публичные страницы для анонима
        (lf('home_url'), lf('anonim_client'), HTTPStatus.OK),
        (lf('login_url'), lf('anonim_client'), HTTPStatus.OK),
        (lf('signup_url'), lf('anonim_client'), HTTPStatus.OK),
        (lf('detail_url'), lf('anonim_client'), HTTPStatus.OK),
        # Доступ к правке/удалению для разных пользователей
        (lf('edit_url'), lf('author_client'), HTTPStatus.OK),
        (lf('edit_url'), lf('reader_client'), HTTPStatus.NOT_FOUND),
        (lf('delete_url'), lf('author_client'), HTTPStatus.OK),
        (lf('delete_url'), lf('reader_client'), HTTPStatus.NOT_FOUND),
    ),
)
def test_pages_availability(url, client_obj, expected_status):
    """
    Единый тест для проверки доступности всех страниц разными
    пользователями.
    """
    response = client_obj.get(url)
    assert response.status_code == expected_status


def test_anonim_logout_availability(logout_url, anonim_client):
    """Тест для проверки возможности выхода анонимному пользователю."""
    response = anonim_client.post(logout_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url',
    (lf('edit_url'), lf('delete_url')),
)
def test_redirects_for_anonymous_user(anonim_client, url, login_url):
    """Проверка перенаправления анонимного пользователя."""
    expected_url = f'{login_url}?next={url}'
    response = anonim_client.get(url)
    assertRedirects(response, expected_url)
