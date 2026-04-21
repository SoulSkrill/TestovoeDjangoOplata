from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Currency, Discount, Item, Order


@override_settings(
    STRIPE_DEFAULT_CURRENCY="usd",
    STRIPE_KEYPAIRS={
        "usd": {"secret": "sk_test_usd", "publishable": "pk_test_usd"},
        "rub": {"secret": "sk_test_rub", "publishable": "pk_test_rub"},
    },
)
class PaymentViewsTests(TestCase):
    def setUp(self):
        self.item = Item.objects.create(
            name="Test item",
            description="Simple description",
            price="10.00",
            currency=Currency.USD,
        )

    def test_item_page(self):
        response = self.client.get(reverse("item-page", args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.item.name)
        self.assertContains(response, "buy-button")

    def test_order_page(self):
        discount = Discount.objects.create(name="Ten", stripe_coupon_id="coupon_1", percent_off="10.00")
        order = Order.objects.create(title="Order #1", discount=discount)
        order.items.add(self.item)

        response = self.client.get(reverse("order-page", args=[order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Сумма без скидки")
        self.assertContains(response, "Сумма со скидкой")

    @patch("payments.views.stripe.checkout.Session.create")
    def test_buy_item(self, create_session_mock):
        create_session_mock.return_value.id = "cs_test_123"
        response = self.client.get(reverse("buy-item", args=[self.item.id]))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"id": "cs_test_123"})
        self.assertTrue(create_session_mock.called)

    @patch("payments.views.stripe.checkout.Session.create")
    def test_buy_order(self, create_session_mock):
        create_session_mock.return_value.id = "cs_test_order"
        order = Order.objects.create(title="Order #1")
        order.items.add(self.item)

        response = self.client.get(reverse("buy-order", args=[order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"id": "cs_test_order"})

    @patch("payments.views.stripe.PaymentIntent.create")
    def test_buy_intent(self, create_intent_mock):
        create_intent_mock.return_value.client_secret = "pi_secret"
        response = self.client.get(reverse("buy-intent", args=[self.item.id]))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"client_secret": "pi_secret"})
