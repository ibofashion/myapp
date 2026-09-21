import pytest
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory

from core.authz import admin_required, can_edit_sale, is_admin
from core.models import Client, Sale, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def client_obj():
    return Client.objects.create(name="Awa Traoré", phone="+237671234567")


@pytest.fixture
def sale(client_obj):
    seller = User.objects.create_user(username="vendeur1", password="x", role="vendeur")
    return Sale.objects.create(client=client_obj, seller=seller)


def test_le_vendeur_proprietaire_peut_modifier_sa_vente(sale):
    assert can_edit_sale(sale.seller, sale) is True


def test_un_admin_peut_modifier_nimporte_quelle_vente(sale):
    admin = User.objects.create_user(username="admin1", password="x", role="admin")
    assert can_edit_sale(admin, sale) is True


def test_un_vendeur_tiers_ne_peut_pas_modifier_la_vente(sale):
    other = User.objects.create_user(username="vendeur2", password="x", role="vendeur")
    assert can_edit_sale(other, sale) is False


def test_is_admin_vrai_pour_un_admin():
    admin = User.objects.create_user(username="admin1", password="x", role="admin")
    assert is_admin(admin) is True


def test_is_admin_faux_pour_un_vendeur():
    vendeur = User.objects.create_user(username="vendeur1", password="x", role="vendeur")
    assert is_admin(vendeur) is False


def test_admin_required_refuse_un_vendeur():
    request = RequestFactory().get("/")
    request.user = User(username="vendeur1", role="vendeur")

    @admin_required
    def view(request):
        return "ok"

    with pytest.raises(PermissionDenied):
        view(request)


def test_admin_required_laisse_passer_un_admin():
    request = RequestFactory().get("/")
    request.user = User(username="admin1", role="admin")

    @admin_required
    def view(request):
        return "ok"

    assert view(request) == "ok"
