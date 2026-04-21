from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Sum


class Currency(models.TextChoices):
    USD = "usd", "USD"
    RUB = "rub", "RUB"


class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.USD)

    def __str__(self) -> str:
        return f"{self.name} ({self.currency.upper()})"

    def amount_minor_units(self) -> int:
        return int((self.price * Decimal("100")).quantize(Decimal("1")))


class Discount(models.Model):
    name = models.CharField(max_length=255)
    stripe_coupon_id = models.CharField(max_length=255, unique=True)
    percent_off = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.01")), MaxValueValidator(Decimal("100.00"))],
        help_text="Optional percent value used to display discounted order total in Django admin",
    )

    def __str__(self) -> str:
        return self.name


class Tax(models.Model):
    name = models.CharField(max_length=255)
    stripe_tax_rate_id = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class Order(models.Model):
    title = models.CharField(max_length=255)
    items = models.ManyToManyField(Item, related_name="orders")
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title

    @property
    def total_amount(self) -> Decimal:
        total = self.items.aggregate(total=Sum("price"))["total"]
        return total or Decimal("0.00")

    @property
    def total_amount_with_discount(self) -> Decimal:
        total = self.total_amount
        if not self.discount or self.discount.percent_off is None:
            return total

        discount_amount = (total * self.discount.percent_off / Decimal("100")).quantize(Decimal("0.01"))
        result = (total - discount_amount).quantize(Decimal("0.01"))
        return max(result, Decimal("0.00"))

    @property
    def currency(self) -> str | None:
        values = list(self.items.values_list("currency", flat=True).distinct())
        if len(values) == 1:
            return values[0]
        return None
