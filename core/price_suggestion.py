from core.models import SaleLine


def get_last_price_for_label(label):
    """Dernier prix unitaire pratiqué pour un article de nom exactement `label`."""
    row = (
        SaleLine.objects.filter(label=label)
        .order_by("-sale__sold_at")
        .values("unit_price")
        .first()
    )
    return row["unit_price"] if row else None
