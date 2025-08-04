from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_key',
    (
        'HOME',
        'NEWS_DETAIL',
        'LOGIN',
        'SIGNUP',
        'LOGOUT'
    )
)
def test_pages_availability_for_anonymous_user(url_key, client, urls):
    """Тест доступности страниц для неавторизованных пользователей."""
    if url_key == 'LOGOUT':
        response = client.post(urls[url_key])
    else:
        response = client.get(urls[url_key])
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_clients, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND)
    )
)
@pytest.mark.parametrize(
    'url_key',
    (
        'EDIT',
        'DELETE'
    )
)
def test_availability_for_different_users(
    parametrized_clients, expected_status, url_key, urls
):
    """Тест доступности страниц для разных пользователей."""
    response = parametrized_clients.get(urls[url_key])
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_key',
    (
        'EDIT',
        'DELETE'
    )
)
def test_redirects_for_anonymous_users(url_key, client, urls):
    """Тест редиректов для неавторизованных пользователей."""
    response = client.get(urls[url_key])
    expected_url = f'{urls['LOGIN']}?next={urls[url_key]}'
    assertRedirects(response, expected_url)
