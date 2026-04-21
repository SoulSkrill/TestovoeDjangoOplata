import stripe
from django.conf import settings
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from .models import Item, Order
from .stripe_utils import get_stripe_keys


@require_GET
def home_page(request):
    sample_item = Item.objects.order_by("id").first()
    sample_order = Order.objects.order_by("id").first()
    return render(
        request,
        "payments/home.html",
        {
            "sample_item": sample_item,
            "sample_order": sample_order,
        },
    )


def _build_item_line(item: Item, tax_rate_id: str | None = None) -> dict:
    line = {
        "price_data": {
            "currency": item.currency,
            "product_data": {
                "name": item.name,
                "description": item.description,
            },
            "unit_amount": item.amount_minor_units(),
        },
        "quantity": 1,
    }
    if tax_rate_id:
        line["tax_rates"] = [tax_rate_id]
    return line


def _stripe_session(success_path: str, cancel_path: str, line_items: list[dict], currency: str, discounts: list[dict] | None = None) -> stripe.checkout.Session:
    secret_key, _ = get_stripe_keys(currency)
    if not secret_key:
        raise ValueError(f"Stripe secret key is missing for currency '{currency}'")

    payload = {
        "line_items": line_items,
        "mode": "payment",
        "success_url": f"{settings.DOMAIN_URL}{success_path}",
        "cancel_url": f"{settings.DOMAIN_URL}{cancel_path}",
    }

    if discounts:
        payload["discounts"] = discounts

    return stripe.checkout.Session.create(api_key=secret_key, **payload)


@require_GET
def item_page(request, item_id: int):
    item = get_object_or_404(Item, id=item_id)
    _, publishable_key = get_stripe_keys(item.currency)
    if not publishable_key:
        raise Http404("Stripe publishable key is not configured")

    return render(
        request,
        "payments/item.html",
        {
            "item": item,
            "publishable_key": publishable_key,
        },
    )


@require_GET
def order_page(request, order_id: int):
    order = get_object_or_404(Order.objects.prefetch_related("items", "discount"), id=order_id)
    currency = order.currency
    if not currency:
        return JsonResponse({"detail": "Order must contain items with the same currency"}, status=400)

    _, publishable_key = get_stripe_keys(currency)
    if not publishable_key:
        raise Http404("Stripe publishable key is not configured")

    return render(
        request,
        "payments/order.html",
        {
            "order": order,
            "publishable_key": publishable_key,
            "currency": currency,
        },
    )


@require_GET
def buy_item(request, item_id: int):
    item = get_object_or_404(Item, id=item_id)
    session = _stripe_session(
        success_path=f"/item/{item.id}/?status=success",
        cancel_path=f"/item/{item.id}/?status=cancel",
        line_items=[_build_item_line(item)],
        currency=item.currency,
    )
    return JsonResponse({"id": session.id})


@require_GET
def buy_order(request, order_id: int):
    order = get_object_or_404(Order.objects.prefetch_related("items", "tax", "discount"), id=order_id)
    items = list(order.items.all())

    if not items:
        return JsonResponse({"detail": "Order is empty"}, status=400)

    currency = order.currency
    if not currency:
        return JsonResponse({"detail": "Order must contain items with the same currency"}, status=400)

    tax_rate_id = order.tax.stripe_tax_rate_id if order.tax else None
    line_items = [_build_item_line(item, tax_rate_id=tax_rate_id) for item in items]
    discounts = [{"coupon": order.discount.stripe_coupon_id}] if order.discount else None
    session = _stripe_session(
        success_path=f"/order/{order.id}/?status=success",
        cancel_path=f"/order/{order.id}/?status=cancel",
        line_items=line_items,
        currency=currency,
        discounts=discounts,
    )

    return JsonResponse({"id": session.id})


@require_GET
def buy_item_payment_intent(request, item_id: int):
    item = get_object_or_404(Item, id=item_id)
    secret_key, _ = get_stripe_keys(item.currency)
    if not secret_key:
        return JsonResponse({"detail": f"Missing stripe key for '{item.currency}'"}, status=500)

    intent = stripe.PaymentIntent.create(
        api_key=secret_key,
        amount=item.amount_minor_units(),
        currency=item.currency,
        description=f"Payment for item #{item.id}: {item.name}",
        metadata={"item_id": str(item.id)},
        automatic_payment_methods={"enabled": True},
    )
    return JsonResponse({"client_secret": intent.client_secret})
