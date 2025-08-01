from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', lf('news_pk_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None)

    )
)
def test_pages_availability_for_anonymous_user(name, args, client):
    """Тест доступности страниц для неавторизованных пользователей."""
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
        'parametrized_clients, expected_status',
        (
            (lf('author_client'), HTTPStatus.OK),
            (lf('not_author_client'), HTTPStatus.NOT_FOUND)
        )
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_availability_for_different_users(
    parametrized_clients, expected_status, name, news, comment
):
    """Тест доступности страниц для разных пользователей."""
    url = reverse(name, args=(comment.id,))
    response = parametrized_clients.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_redirects_for_anonymous_users(name, comment, client):
    """Тест редиректов для неавторизованных пользователей."""
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    response = client.get(url)
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
