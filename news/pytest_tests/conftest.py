import pytest
from django.test.client import Client

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    """Фикстура для создания модели автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Фикстура для создания модели другого пользователя."""
    return django_user_model.objects.create(username='Другой пользователь')


@pytest.fixture
def author_client(author):
    """Фикстура для создания клиента автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Фикстура для создания клиента другого пользователя."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Фикстура для создания новости."""
    news = News.objects.create(
        title='Заголовок',
        text='Текст.'
    )
    return news


@pytest.fixture
def comment(author, news):
    """Фикстура для создания комментария."""
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def news_pk_for_args(news):
    """Фикстура возвращает news_pk."""
    return (news.pk,)
