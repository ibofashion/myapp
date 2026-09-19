import pytest
from django.test import Client as DjangoClient
from django.urls import reverse

from core.models import Client, Sale, SaleLine, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def client_obj():
    return Client.objects.create(name="Awa Traoré", phone="+237671234567")


@pytest.fixture
def sale(client_obj):
    seller = User.objects.create_user(username="vendeur1", password="x", role="vendeur")
    sale = Sale.objects.create(client=client_obj, seller=seller)
    SaleLine.objects.create(sale=sale, label="Sac de riz", unit_price=1500, quantity=3)
    return sale


def edit_formset_data(sale, *, label="Sac de riz", unit_price="1500", quantity="3", delete=False):
    line = sale.lines.get()
    data = {
        "lines-TOTAL_FORMS": "1",
        "lines-INITIAL_FORMS": "1",
        "lines-MIN_NUM_FORMS": "1",
        "lines-MAX_NUM_FORMS": "1000",
        "lines-0-id": str(line.id),
        "lines-0-label": label,
        "lines-0-unit_price": unit_price,
        "lines-0-quantity": quantity,
    }
    if delete:
        data["lines-0-DELETE"] = "on"
    return data


def test_le_vendeur_dorigine_modifie_sa_vente(sale):
    web = DjangoClient()
    web.login(username="vendeur1", password="x")

    response = web.post(reverse("sale_edit", args=[sale.pk]), edit_formset_data(sale, unit_price="2000"))

    assert response.status_code == 200
    sale.refresh_from_db()
    assert sale.lines.get().unit_price == 2000
    assert sale.total == 6000


def test_un_admin_modifie_la_vente_dun_autre_vendeur(sale):
    User.objects.create_user(username="admin1", password="x", role="admin")
    web = DjangoClient()
    web.login(username="admin1", password="x")

    response = web.post(reverse("sale_edit", args=[sale.pk]), edit_formset_data(sale, quantity="5"))

    assert response.status_code == 200
    sale.refresh_from_db()
    assert sale.lines.get().quantity == 5


def test_modification_vidant_toutes_les_lignes_refusee(sale):
    web = DjangoClient()
    web.login(username="vendeur1", password="x")

    response = web.post(reverse("sale_edit", args=[sale.pk]), edit_formset_data(sale, delete=True))

    assert response.status_code == 200
    assert sale.lines.count() == 1
    assert "please submit at least 1 form" in response.content.decode().lower()


def test_un_vendeur_tiers_ne_peut_pas_modifier_la_vente(sale):
    User.objects.create_user(username="vendeur2", password="x", role="vendeur")
    web = DjangoClient()
    web.login(username="vendeur2", password="x")

    response = web.post(reverse("sale_edit", args=[sale.pk]), edit_formset_data(sale, unit_price="9999"))

    assert response.status_code == 403
    sale.refresh_from_db()
    assert sale.lines.get().unit_price == 1500
