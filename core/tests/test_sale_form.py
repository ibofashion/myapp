import pytest

from core.forms import SaleForm, SaleLineFormSet
from core.models import Client, Sale

pytestmark = pytest.mark.django_db


def formset_management_data(total=1, initial=0):
    return {
        "lines-TOTAL_FORMS": str(total),
        "lines-INITIAL_FORMS": str(initial),
        "lines-MIN_NUM_FORMS": "1",
        "lines-MAX_NUM_FORMS": "1000",
    }


@pytest.fixture
def client_obj():
    return Client.objects.create(name="Awa Traoré", phone="+237671234567")


def test_sale_without_client_rejected():
    form = SaleForm(data={})
    assert not form.is_valid()
    assert "client" in form.errors


def test_sale_without_any_line_rejected(client_obj):
    sale = Sale(client=client_obj)
    data = formset_management_data(total=1)
    data.update({
        "lines-0-label": "",
        "lines-0-unit_price": "",
        "lines-0-quantity": "",
    })
    formset = SaleLineFormSet(data=data, instance=sale, prefix="lines")
    assert not formset.is_valid()


def test_line_with_invalid_quantity_rejected(client_obj):
    sale = Sale(client=client_obj)
    data = formset_management_data(total=1)
    data.update({
        "lines-0-label": "Sac de riz",
        "lines-0-unit_price": "1500",
        "lines-0-quantity": "0",
    })
    formset = SaleLineFormSet(data=data, instance=sale, prefix="lines")
    assert not formset.is_valid()
    assert "quantity" in formset.forms[0].errors


def test_line_with_negative_price_rejected(client_obj):
    sale = Sale(client=client_obj)
    data = formset_management_data(total=1)
    data.update({
        "lines-0-label": "Sac de riz",
        "lines-0-unit_price": "-100",
        "lines-0-quantity": "2",
    })
    formset = SaleLineFormSet(data=data, instance=sale, prefix="lines")
    assert not formset.is_valid()
    assert "unit_price" in formset.forms[0].errors


def test_valid_lines_accepted(client_obj):
    sale = Sale(client=client_obj)
    data = formset_management_data(total=2)
    data.update({
        "lines-0-label": "Sac de riz",
        "lines-0-unit_price": "1500",
        "lines-0-quantity": "3",
        "lines-1-label": "Huile",
        "lines-1-unit_price": "2000",
        "lines-1-quantity": "1",
    })
    formset = SaleLineFormSet(data=data, instance=sale, prefix="lines")
    assert formset.is_valid(), formset.errors
