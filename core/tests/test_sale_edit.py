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


def test_double_soumission_apres_ajout_de_ligne_ne_cree_pas_de_doublon(sale):
    web = DjangoClient()
    web.login(username="vendeur1", password="x")
    url = reverse("sale_edit", args=[sale.pk])

    existing_line = sale.lines.get()
    new_line_data = {
        "lines-TOTAL_FORMS": "2",
        "lines-INITIAL_FORMS": "1",
        "lines-MIN_NUM_FORMS": "1",
        "lines-MAX_NUM_FORMS": "1000",
        "lines-0-id": str(existing_line.id),
        "lines-0-label": existing_line.label,
        "lines-0-unit_price": str(existing_line.unit_price),
        "lines-0-quantity": str(existing_line.quantity),
        "lines-1-id": "",
        "lines-1-label": "Sucre",
        "lines-1-unit_price": "700",
        "lines-1-quantity": "2",
    }

    first_response = web.post(url, new_line_data)
    assert first_response.status_code == 200
    assert sale.lines.count() == 2

    # The client re-submits the exact same rendered form a second time
    # (e.g. clicking "Enregistrer" again). The response to the first POST
    # must have refreshed the formset's management form (INITIAL_FORMS) and
    # the new line's hidden id, otherwise this second submit is treated as
    # yet another new line and duplicates it.
    new_line = sale.lines.exclude(pk=existing_line.pk).get()
    second_response = web.post(
        url,
        {
            **new_line_data,
            "lines-INITIAL_FORMS": "2",
            "lines-1-id": str(new_line.pk),
        },
    )

    assert second_response.status_code == 200
    assert sale.lines.count() == 2
    assert sale.lines.filter(label="Sucre").count() == 1


def test_suppression_dune_ligne_vide_ajoutee_par_erreur(sale):
    web = DjangoClient()
    web.login(username="vendeur1", password="x")
    url = reverse("sale_edit", args=[sale.pk])

    existing_line = sale.lines.get()
    data = {
        "lines-TOTAL_FORMS": "2",
        "lines-INITIAL_FORMS": "1",
        "lines-MIN_NUM_FORMS": "1",
        "lines-MAX_NUM_FORMS": "1000",
        "lines-0-id": str(existing_line.id),
        "lines-0-label": existing_line.label,
        "lines-0-unit_price": str(existing_line.unit_price),
        "lines-0-quantity": str(existing_line.quantity),
        "lines-1-id": "",
        "lines-1-label": "",
        "lines-1-unit_price": "",
        "lines-1-quantity": "",
        "lines-1-DELETE": "on",
    }

    response = web.post(url, data)

    assert response.status_code == 200
    assert "obligatoire" not in response.content.decode().lower()
    assert sale.lines.count() == 1
