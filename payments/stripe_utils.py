from django.conf import settings


def get_stripe_keys(currency: str) -> tuple[str, str]:
    normalized = currency.lower()
    pair = settings.STRIPE_KEYPAIRS.get(normalized)

    if pair and pair.get("secret") and pair.get("publishable"):
        return pair["secret"], pair["publishable"]

    fallback = settings.STRIPE_KEYPAIRS.get(settings.STRIPE_DEFAULT_CURRENCY, {})
    secret = fallback.get("secret", "")
    publishable = fallback.get("publishable", "")
    return secret, publishable
