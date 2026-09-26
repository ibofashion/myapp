import pytest

from core.models import Client, Sale, SaleLine, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def client_obj():
    return Client.objects.create(name="Awa Traoré", phone="+237671234567")


@pytest.fixture
def seller():
    return User.objects.create(username="boutique", role="admin")


def test_line_total_is_unit_price_times_quantity(client_obj, seller):
    sale = Sale.objects.create(client=client_obj, seller=seller)
    line = SaleLine.objects.create(sale=sale, label="Sac de riz", unit_price=1500, quantity=3)
    assert line.total == 4500


def test_sale_total_is_sum_of_line_totals(client_obj, seller):
    sale = Sale.objects.create(client=client_obj, seller=seller)
    SaleLine.objects.create(sale=sale, label="Sac de riz", unit_price=1500, quantity=3)
    SaleLine.objects.create(sale=sale, label="Huile", unit_price=2000, quantity=1)
    assert sale.total == 6500
