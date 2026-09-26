import uuid
from collections import defaultdict
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from core.models import Payment, PaymentAllocation, Sale, SaleBalance


@transaction.atomic
def record_payment(*, client, amount, allocations, recorded_by, idempotency_key=None) -> Payment:
    """Enregistre un paiement pour `client` et l'impute sur ses ventes.

    `allocations` est une liste de tuples (Sale, Decimal). Voir ARCHITECTURE.md §4.1 :
    verrouille les ventes ciblées pour que la validation des invariants ci-dessous
    tienne même sous accès concurrent.
    """
    amount = Decimal(amount)
    if amount <= 0:
        raise ValidationError("Le montant du paiement doit être positif.")

    if not allocations:
        raise ValidationError("Au moins une imputation est requise.")

    per_sale_amount: dict[int, Decimal] = defaultdict(lambda: Decimal(0))
    for sale, alloc_amount in allocations:
        alloc_amount = Decimal(alloc_amount)
        if alloc_amount <= 0:
            raise ValidationError("Chaque imputation doit être strictement positive.")
        per_sale_amount[sale.id] += alloc_amount

    total_allocated = sum(per_sale_amount.values(), start=Decimal(0))
    if total_allocated != amount:
        raise ValidationError("Le montant réparti ne correspond pas au montant du paiement.")

    sale_ids = list(per_sale_amount.keys())
    locked_sales = {
        sale.id: sale
        for sale in Sale.objects.select_for_update()
        .filter(id__in=sale_ids, client=client)
        .order_by("id")
    }
    if set(locked_sales.keys()) != set(sale_ids):
        raise ValidationError("Une vente sélectionnée n'appartient pas à ce client.")

    balances = {
        balance.sale_id: balance.balance
        for balance in SaleBalance.objects.filter(sale_id__in=sale_ids)
    }
    for sale_id, alloc_amount in per_sale_amount.items():
        remaining = balances.get(sale_id, Decimal(0))
        if alloc_amount > remaining:
            raise ValidationError(
                f"Le montant imputé dépasse le solde restant de la vente #{sale_id}."
            )

    payment = Payment.objects.create(
        client=client,
        amount=amount,
        recorded_by=recorded_by,
        idempotency_key=idempotency_key or uuid.uuid4(),
    )
    PaymentAllocation.objects.bulk_create(
        [
            PaymentAllocation(payment=payment, sale=locked_sales[sale_id], amount=alloc_amount)
            for sale_id, alloc_amount in per_sale_amount.items()
        ]
    )
    return payment
