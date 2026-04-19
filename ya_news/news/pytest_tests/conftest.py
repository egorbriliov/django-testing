import pytest
from django.test import Client
from django.urls import reverse
from news.models import Comment, News

from ya_news.yanews import settings


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture(autouse=True)
def many_news(db):
    return News.objects.bulk_create(
        News(title=f'Title {index}', text='text')
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE * 2)
    )


@pytest.fixture(autouse=True)
def many_comments(author, db):
    news = News.objects.create(title='title', text='text')
    return Comment.objects.bulk_create(
        Comment(
            news=news,
            author=author,
            text=f'Comment #{index}'
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


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
    return News.objects.first()


@pytest.fixture()
def comment():
    return Comment.objects.first()


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
