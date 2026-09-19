import pytest
from django.test import Client as DjangoClient
from django.urls import reverse

from core.models import Client, Sale, SaleLine, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def seller():
    return User.objects.create_user(username="vendeur1", password="x", role="vendeur")


@pytest.fixture
def client_obj():
    return Client.objects.create(name="Awa Traoré", phone="+237671234567")


@pytest.fixture
def sale_obj(client_obj, seller):
    sale = Sale.objects.create(client=client_obj, seller=seller)
    SaleLine.objects.create(sale=sale, label="Article", unit_price=10000, quantity=1)
    return sale


def functional_urls(client_obj, sale_obj):
    return {
        "home": reverse("home"),
        "client_list": reverse("client_list"),
        "client_create": reverse("client_create"),
        "client_detail": reverse("client_detail", args=[client_obj.pk]),
        "sale_create": reverse("sale_create"),
        "sale_detail": reverse("sale_detail", args=[sale_obj.pk]),
    }


def test_pages_fonctionnelles_redirigent_vers_login_sans_session(client_obj, sale_obj):
    web = DjangoClient()
    login_url = reverse("login")

    for name, url in functional_urls(client_obj, sale_obj).items():
        response = web.get(url)
        assert response.status_code == 302, f"{name} devrait rediriger sans session"
        assert response.url.startswith(login_url), f"{name} devrait rediriger vers la connexion"


def test_pages_fonctionnelles_accessibles_avec_session(client_obj, sale_obj, seller):
    web = DjangoClient()
    web.login(username="vendeur1", password="x")

    for name, url in functional_urls(client_obj, sale_obj).items():
        response = web.get(url)
        assert response.status_code == 200, f"{name} devrait être accessible connecté"


def test_identifiants_invalides_refuses():
    web = DjangoClient()
    response = web.post(reverse("login"), {"username": "inconnu", "password": "mauvais"})
    assert response.status_code == 200
    assert response.wsgi_request.user.is_authenticated is False


def test_deconnexion_redirige_vers_login(seller):
    web = DjangoClient()
    web.login(username="vendeur1", password="x")
    response = web.post(reverse("logout"))
    assert response.status_code == 302
    assert response.url == reverse("login")

    response = web.get(reverse("home"))
    assert response.status_code == 302
