from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


FORM_DATA = {'text': 'Новый текст'}

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, urls):
    """Тест невозможности создать комментарий анонимным пользователем."""
    comments_count_before = Comment.objects.count()
    response = client.post(urls['NEWS_DETAIL'], data=FORM_DATA)
    expected_url = f'{urls['LOGIN']}?next={urls['NEWS_DETAIL']}'
    assertRedirects(response, expected_url)
    comments_count_after = Comment.objects.count()
    assert comments_count_before == comments_count_after


def test_user_can_create_comment(author, author_client, news, urls):
    """Тест возможности создать комментарий автором."""
    comments_count_before = Comment.objects.count()
    response = author_client.post(urls['NEWS_DETAIL'], data=FORM_DATA)
    assertRedirects(response, f'{urls['NEWS_DETAIL']}#comments')
    comments_count_after = Comment.objects.count()
    assert comments_count_before != comments_count_after
    new_comment = Comment.objects.latest('id')
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.news == news
    assert new_comment.author == author


def test_user_cant_use_bad_words(news, author_client, urls):
    """Тест невозможности использовать запрещенные слова."""
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    comments_count_before = Comment.objects.count()
    response = author_client.post(urls['NEWS_DETAIL'], data=bad_words_data)
    comments_count_after = Comment.objects.count()
    assertFormError(
        response.context['form'],
        'text',
        errors=(WARNING)
    )
    assert comments_count_before == comments_count_after


def test_author_can_delete_comment(author_client, comment, news, urls):
    """Тест возможности удаления комментария автором."""
    comments_count_before = Comment.objects.count()
    response = author_client.post(urls['DELETE'])
    comments_count_after = Comment.objects.count()
    assertRedirects(response, f'{urls['NEWS_DETAIL']}#comments')
    assert comments_count_before != comments_count_after


def test_user_cant_delete_comment_of_another_user(
    not_author_client, comment, news, urls
):
    """Тест невозможности удаления комментария не автором."""
    comments_count_before = Comment.objects.count()
    response = not_author_client.post(urls['DELETE'])
    comments_count_after = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comments_count_before == comments_count_after


def test_author_can_edit_comment(author_client, comment, news, urls):
    """Тест возможности изменять комментарий автором."""
    response = author_client.post(urls['EDIT'], data=FORM_DATA)
    assertRedirects(response, f'{urls['NEWS_DETAIL']}#comments')
    comment.refresh_from_db()
    assert comment.text == FORM_DATA['text']


def test_user_cant_edit_comment_of_another_user(
    not_author_client, comment, news, urls
):
    """Тест невозможности изменять комментарий не автором."""
    response = not_author_client.post(urls['EDIT'], data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.latest('id')
    assert comment.text == comment_from_db.text
