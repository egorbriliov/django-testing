import pytest
from django.test import Client
from django.urls import reverse

from yanews import settings
from news.models import Comment, News


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def anonim_client():
    return Client()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture()
def news():
    if not News.objects.exists():
        News.objects.create(title='title', text='text')
    return News.objects.first()


@pytest.fixture()
def many_news():
    return News.objects.bulk_create(
        News(title=f'Title {index}', text='text')
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE * 2)
    )


@pytest.fixture()
def comment(news, author):
    if not Comment.objects.exists():
        Comment.objects.create(news=news, text='text', author=author)
    return Comment.objects.first()


@pytest.fixture()
def many_comments(author, news):
    return Comment.objects.bulk_create(
        Comment(
            news=news,
            author=author,
            text=f'Comment #{index}'
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))
