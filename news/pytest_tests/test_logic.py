from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news):
    """Тест невозможности создать комментарий анонимным пользователем."""
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(author, author_client, form_data, news):
    """Тест возможности создать комментарий автором."""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.news == news
    assert new_comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(news, author_client):
    """Тест невозможности использовать запрещенные слова."""
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response.context['form'],
        'text',
        errors=(WARNING)
    )
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment, news):
    """Тест возможности удаления комментария автором."""
    url = reverse('news:detail', args=(news.id,))
    url_delete = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url_delete)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
    not_author_client, comment, news
):
    """Тест невозможности удаления комментария не автором."""
    url_delete = reverse('news:delete', args=(comment.id,))
    response = not_author_client.post(url_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment, news, form_data):
    """Тест возможности изменять комментарий автором."""
    url = reverse('news:detail', args=(news.id,))
    url_edit = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url_edit, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
    not_author_client, comment, news, form_data
):
    """Тест невозможности изменять комментарий не автором."""
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
