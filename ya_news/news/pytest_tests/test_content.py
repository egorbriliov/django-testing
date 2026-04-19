from django.urls import reverse

import pytest
from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(news, author_client):
    """Тестировние количества выводимых новостей на главную страницу."""
    url = reverse('news:home')
    response = author_client.get(url)
    news = response.context['object_list']
    assert news.count() <= 10


@pytest.mark.django_db
def test_news_order(news, author_client):
    """Тестирование сортировки новостей от новых к старым."""
    url = reverse('news:home')
    response = author_client.get(url)
    news = response.context['object_list']
    sorted_news = sorted(news, key=lambda news: news.date, reverse=True)
    for old, new in zip(news, sorted_news):
        assert old.date == new.date


@pytest.mark.django_db
def test_comments_order(news, author_client):
    """Тестирвоание комментриев от начального к конечному."""
    url = reverse('news:detail', args=(news.pk, ))
    response = author_client.get(url)
    comments = response.context['news'].comment_set.all()
    sorted_comments = sorted(comments, key=lambda comment: comment.date)
    for old, new in zip(comments, sorted_comments):
        assert old.date == new.date


@pytest.mark.parametrize(
    'target_client, available',
    ((pytest.lazy_fixture('admin_client'), True),  # type: ignore
     (pytest.lazy_fixture('client'), False))  # type: ignore
)
@pytest.mark.django_db
def test_comment_form_availability_for_different_users(
        news_pk, target_client, available):
    """Тестирование доступности формы для различных пользователей."""
    url = reverse('news:detail', args=news_pk)
    response = target_client.get(url)
    assert ('form' in response.context) is available
    if available:
        assert isinstance(response.context['form'], CommentForm)
