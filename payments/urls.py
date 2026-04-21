from django.urls import path

from .views import buy_item, buy_item_payment_intent, buy_order, item_page, order_page

urlpatterns = [
    path("item/<int:item_id>/", item_page, name="item-page"),
    path("order/<int:order_id>/", order_page, name="order-page"),
    path("buy/<int:item_id>/", buy_item, name="buy-item"),
    path("buy-order/<int:order_id>/", buy_order, name="buy-order"),
    path("buy-intent/<int:item_id>/", buy_item_payment_intent, name="buy-intent"),
]
