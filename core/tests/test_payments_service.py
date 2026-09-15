import pytest
from django.core.exceptions import ValidationError

from core.models import (
    Client,
    Payment,
    PaymentAllocation,
    Sale,
    SaleBalance,
    SaleLine,
    User,
)
from core.payments import record_payment

pytestmark = pytest.mark.django_db


@pytest.fixture
def seller():
    return User.objects.create(username="boutique", role="admin")


@pytest.fixture
def client_obj():
    return Client.objects.create(name="Awa Traoré", phone="+237671234567")


@pytest.fixture
def other_client():
    return Client.objects.create(name="Autre Client", phone="+237699000000")


def make_sale(client_obj, seller, total):
    sale = Sale.objects.create(client=client_obj, seller=seller)
    SaleLine.objects.create(sale=sale, label="Article", unit_price=total, quantity=1)
    return sale


def balance_of(sale):
    return SaleBalance.objects.get(sale_id=sale.id)


def test_paiement_valide_cree_payment_et_allocation(client_obj, seller):
    sale = make_sale(client_obj, seller, 10000)

    payment = record_payment(
        client=client_obj, amount=4000, allocations=[(sale, 4000)], recorded_by=seller
    )

    assert Payment.objects.count() == 1
    assert PaymentAllocation.objects.filter(payment=payment, sale=sale, amount=4000).exists()
    assert balance_of(sale).balance == 6000
    assert balance_of(sale).status == "partiel"


def test_imputation_repartie_sur_plusieurs_ventes(client_obj, seller):
    sale1 = make_sale(client_obj, seller, 5000)
    sale2 = make_sale(client_obj, seller, 5000)

    record_payment(
        client=client_obj,
        amount=7000,
        allocations=[(sale1, 3000), (sale2, 4000)],
        recorded_by=seller,
    )

    assert balance_of(sale1).balance == 2000
    assert balance_of(sale2).balance == 1000


def test_repartition_incomplete_rejetee(client_obj, seller):
    sale = make_sale(client_obj, seller, 10000)

    with pytest.raises(ValidationError):
        record_payment(
            client=client_obj, amount=10000, allocations=[(sale, 6000)], recorded_by=seller
        )
    assert Payment.objects.count() == 0


def test_repartition_excedentaire_rejetee(client_obj, seller):
    sale1 = make_sale(client_obj, seller, 10000)
    sale2 = make_sale(client_obj, seller, 10000)

    with pytest.raises(ValidationError):
        record_payment(
            client=client_obj,
            amount=5000,
            allocations=[(sale1, 3000), (sale2, 3000)],
            recorded_by=seller,
        )
    assert Payment.objects.count() == 0


def test_depassement_solde_restant_rejete(client_obj, seller):
    sale = make_sale(client_obj, seller, 10000)

    with pytest.raises(ValidationError):
        record_payment(
            client=client_obj, amount=10001, allocations=[(sale, 10001)], recorded_by=seller
        )
    assert Payment.objects.count() == 0
    assert balance_of(sale).balance == 10000


def test_imputation_nulle_rejetee(client_obj, seller):
    sale = make_sale(client_obj, seller, 10000)

    with pytest.raises(ValidationError):
        record_payment(client=client_obj, amount=0, allocations=[(sale, 0)], recorded_by=seller)
    assert Payment.objects.count() == 0


def test_vente_dun_autre_client_rejetee(client_obj, other_client, seller):
    sale_other = make_sale(other_client, seller, 5000)

    with pytest.raises(ValidationError):
        record_payment(
            client=client_obj, amount=1000, allocations=[(sale_other, 1000)], recorded_by=seller
        )
    assert Payment.objects.count() == 0


def test_montant_paiement_non_positif_rejete(client_obj, seller):
    sale = make_sale(client_obj, seller, 10000)

    with pytest.raises(ValidationError):
        record_payment(client=client_obj, amount=-1, allocations=[(sale, -1)], recorded_by=seller)


def test_fumee_architecture_solde_progressif(client_obj, seller):
    """ARCHITECTURE.md §8, points 1 à 4."""
    sale = make_sale(client_obj, seller, 10000)
    assert balance_of(sale).balance == 10000
    assert balance_of(sale).status == "non_paye"

    record_payment(client=client_obj, amount=4000, allocations=[(sale, 4000)], recorded_by=seller)
    assert balance_of(sale).balance == 6000
    assert balance_of(sale).status == "partiel"

    record_payment(client=client_obj, amount=6000, allocations=[(sale, 6000)], recorded_by=seller)
    assert balance_of(sale).balance == 0
    assert balance_of(sale).status == "solde"

    with pytest.raises(ValidationError):
        record_payment(client=client_obj, amount=1, allocations=[(sale, 1)], recorded_by=seller)
    assert balance_of(sale).balance == 0
