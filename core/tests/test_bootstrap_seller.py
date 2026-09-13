import pytest
from django.core.management import call_command

from core.models import User

pytestmark = pytest.mark.django_db


def test_bootstrap_seller_is_idempotent():
    call_command("bootstrap_seller")
    call_command("bootstrap_seller")

    assert User.objects.filter(username="boutique", role="admin").count() == 1
