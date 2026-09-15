import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from core.phone import normalize_phone


class User(AbstractUser):
    ROLE_CHOICES = [("vendeur", "Vendeur"), ("admin", "Admin")]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="vendeur")


class Client(models.Model):
    phone = models.CharField(
        max_length=20,
        unique=True,
        error_messages={"unique": "Un client avec ce numéro de téléphone existe déjà."},
    )
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.phone:
            self.phone = normalize_phone(self.phone)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.phone})"


class Sale(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="sales")
    seller = models.ForeignKey(User, on_delete=models.PROTECT, related_name="sales")
    sold_at = models.DateTimeField(auto_now_add=True)
    idempotency_key = models.UUIDField(unique=True, default=uuid.uuid4)

    @property
    def total(self):
        return sum((line.total for line in self.lines.all()), start=0)

    def __str__(self):
        return f"Vente #{self.pk} — {self.client}"


class SaleLine(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="lines")
    label = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=12, decimal_places=0)
    quantity = models.PositiveIntegerField()

    @property
    def total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.label} x{self.quantity}"


class Payment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    paid_at = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="payments_recorded")
    idempotency_key = models.UUIDField(unique=True, default=uuid.uuid4)

    def __str__(self):
        return f"Paiement #{self.pk} — {self.client} — {self.amount} FCFA"


class PaymentAllocation(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name="allocations")
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name="allocations")
    amount = models.DecimalField(max_digits=12, decimal_places=0)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gt=0), name="allocation_amount_positive"),
        ]

    def __str__(self):
        return f"{self.amount} FCFA sur vente #{self.sale_id}"


class SaleBalance(models.Model):
    """Modèle non managé exposant la vue SQL `v_sale_balances` (voir ARCHITECTURE.md §3).

    Source unique du solde et du statut d'une vente : jamais de champ équivalent
    stocké en dur sur `Sale`, pour ne jamais pouvoir diverger après un paiement.
    """

    STATUS_LABELS = {
        "non_paye": "Non payé",
        "partiel": "Partiel",
        "solde": "Soldé",
    }

    sale = models.OneToOneField(
        Sale, primary_key=True, db_column="sale_id", on_delete=models.DO_NOTHING, related_name="balance"
    )
    client_id = models.IntegerField()
    total = models.DecimalField(max_digits=12, decimal_places=0)
    paid = models.DecimalField(max_digits=12, decimal_places=0)
    balance = models.DecimalField(max_digits=12, decimal_places=0)
    status = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = "v_sale_balances"

    @property
    def status_label(self):
        return self.STATUS_LABELS.get(self.status, self.status)
