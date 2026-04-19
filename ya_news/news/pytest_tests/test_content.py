from news.forms import CommentForm
from yanews import settings


def test_news_count(author_client, home_url):
    """Тестировние количества выводимых новостей на главную страницу."""
    response = author_client.get(home_url)
    news = response.context['object_list']
    assert news.count() <= settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(author_client, home_url):
    """Тестирование сортировки новостей от новых к старым."""
    response = author_client.get(home_url)
    news = response.context['object_list']
    for old, new in zip(news, sorted(news,
                                     key=lambda
                                     news: news.date,
                                     reverse=True)):
        assert old.date == new.date


def test_comments_order(author_client, detail_url):
    """Тестирвоание комментриев от начального к конечному."""
    response = author_client.get(detail_url)
    comments = response.context['news'].comment_set.all()
    sorted_comments = sorted(comments, key=lambda comment: comment.created)
    for old, new in zip(comments, sorted_comments):
        assert old.created == new.created


def test_comment_form_availability_for_auth_user(detail_url, author_client):
    """Тестирование доступности формы для различных пользователей."""
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


def test_comment_form_availability_for_anonim(detail_url, anonim_client):
    """Тестирование доступности формы для анонимного пользователя."""
    response = anonim_client.get(detail_url)
    assert 'form' not in response.context
