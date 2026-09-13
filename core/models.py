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
