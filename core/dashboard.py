from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from core.models import Payment, SaleBalance

DEFAULT_PERIOD = "jour"

PERIOD_LABELS = {
    "jour": "Aujourd'hui",
    "semaine": "Cette semaine",
    "mois": "Ce mois",
}


def get_debt_summary():
    """Dette en cours globale et détaillée par client, dérivée de `SaleBalance`."""
    rows = (
        SaleBalance.objects.filter(balance__gt=0)
        .values("client_id", "sale__client__name")
        .annotate(total_due=Sum("balance"))
        .order_by("sale__client__name")
    )
    debts_by_client = [
        {
            "client_id": row["client_id"],
            "client_name": row["sale__client__name"],
            "total_due": row["total_due"],
        }
        for row in rows
    ]
    total_due = sum((row["total_due"] for row in debts_by_client), start=Decimal(0))
    return total_due, debts_by_client


def get_period_bounds(preset, *, now=None):
    """Bornes [début, fin) du préset demandé, en heure locale du projet."""
    now = now or timezone.localtime(timezone.now())
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if preset == "semaine":
        start = today_start - timezone.timedelta(days=today_start.isoweekday() - 1)
        end = start + timezone.timedelta(days=7)
    elif preset == "mois":
        start = today_start.replace(day=1)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1)
        else:
            end = start.replace(month=start.month + 1)
    else:
        start = today_start
        end = start + timezone.timedelta(days=1)

    return start, end


def get_payments_total(start, end):
    """Somme des paiements enregistrés dans la fenêtre `[start, end)`."""
    total = Payment.objects.filter(paid_at__gte=start, paid_at__lt=end).aggregate(total=Sum("amount"))[
        "total"
    ]
    return total or Decimal(0)
