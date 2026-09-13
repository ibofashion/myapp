import pytest

from core.forms import ClientForm
from core.models import Client

pytestmark = pytest.mark.django_db


def test_valid_submission_creates_client():
    form = ClientForm(data={"name": "Awa Traoré", "phone": "671 23 45 67"})
    assert form.is_valid(), form.errors
    client = form.save()
    assert client.phone == "+237671234567"


def test_missing_phone_rejected():
    form = ClientForm(data={"name": "Awa Traoré", "phone": ""})
    assert not form.is_valid()
    assert "phone" in form.errors


def test_normalized_duplicate_rejected():
    Client.objects.create(name="Awa Traoré", phone="+237671234567")
    form = ClientForm(data={"name": "Autre Nom", "phone": "671-23-45-67"})
    assert not form.is_valid()
    assert "phone" in form.errors
