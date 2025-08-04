import pytest

from django.urls import reverse

from news.forms import CommentForm
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


pytestmark = pytest.mark.django_db


def test_news_count(not_author_client, news_to_pagginate, urls):
    """Тест количества новостей на странице."""
    response = not_author_client.get(urls['HOME'])
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == NEWS_COUNT_ON_HOME_PAGE


def test_news_order(not_author_client, news_to_pagginate, urls):
    """Тест порядка вывода новостей."""
    response = not_author_client.get(urls['HOME'])
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comment_order(news, comment_to_pagginate, not_author_client, urls):
    """Тест порядка вывода комментариев."""
    response = not_author_client.get(urls['NEWS_DETAIL'])
    assert 'news' in response.context
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(news, client, urls):
    """Тест отсутствия формы комментария для неавторизованного пользователя."""
    response = client.get(urls['NEWS_DETAIL'])
    assert 'form' not in response.context


def test_authorized_client_has_form(news, author_client, urls):
    """Тест наличия формы комментария для авторизованного пользователя."""
    response = author_client.get(urls['NEWS_DETAIL'])
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
