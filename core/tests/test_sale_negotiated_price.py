import pytest

from core.models import Client, Sale, SaleLine, User

pytestmark = pytest.mark.django_db


def test_same_label_different_price_on_two_sales_both_kept():
    client_obj = Client.objects.create(name="Awa Traoré", phone="+237671234567")
    seller = User.objects.create(username="boutique", role="admin")

    sale1 = Sale.objects.create(client=client_obj, seller=seller)
    line1 = SaleLine.objects.create(sale=sale1, label="Sac de riz", unit_price=12000, quantity=1)

    sale2 = Sale.objects.create(client=client_obj, seller=seller)
    line2 = SaleLine.objects.create(sale=sale2, label="Sac de riz", unit_price=13500, quantity=1)

    assert line1.unit_price == 12000
    assert line2.unit_price == 13500
