import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


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
def news_to_pagginate():
    """Фикстура для создания новостей."""
    today = timezone.now().date()
    news_to_pagginate = News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timezone.timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return news_to_pagginate


@pytest.fixture
def news():
    """Фикстура для создания новости."""
    return News.objects.create(
        title='Заголовок',
        text='Просто текст.'
    )


@pytest.fixture
def comment(author, news):
    """Фикстура для создания комментария."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def comment_to_pagginate(news, author):
    """Фикстура для создания комментариев."""
    now = timezone.now()
    for index in range(10):
        comment_to_pagginate = Comment.objects.create(
            news=news, author=author, text=f'Текст {index}'
        )
        comment_to_pagginate.created = now + timezone.timedelta(days=index)
        comment_to_pagginate.save()
    return comment_to_pagginate


@pytest.fixture
def urls(news, comment):
    """Фикстура для возврата url адресов."""
    return {
        'HOME': reverse('news:home'),
        'NEWS_DETAIL': reverse('news:detail', args=(news.id,)),
        'LOGIN': reverse('users:login'),
        'SIGNUP': reverse('users:signup'),
        'LOGOUT': reverse('users:logout'),
        'DELETE': reverse('news:delete', args=(comment.id,)),
        'EDIT': reverse('news:edit', args=(comment.id,))
    }
