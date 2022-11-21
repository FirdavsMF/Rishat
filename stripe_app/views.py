import stripe
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from RishatTest.settings import env
from stripe_app.models import Item, Order, Discount, Tax

stripe.api_key = env('STRIPE_API_KEY')


def buy_item(request, item_id):
    """
    Create stripe session ID for item
    :param request:
    :param item_id: id of item
    :return: stripe session_id
    """

    item = Item.objects.get(id=item_id)
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': item.currency,
                        'product_data': {'name': item.name},
                        'unit_amount': item.price * 100,
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='http://localhost:4242/success.html',
            cancel_url='http://localhost:4242/cancel.html',
        )
        return JsonResponse({'session_id': session.id})
    except stripe.error.InvalidRequestError as e:
        return HttpResponse(str(e))


def item_check(request, item_id):
    """
    Get item by id
    :param request:
    :param item_id: id of item
    :return: Return an HttpResponse whose content is filled with the result
    """

    item = Item.objects.get(id=item_id)
    return render(request, 'item.html', model_to_dict(item))


def add_items_to_order(order, items_ids):
    """
    Add items to order
    :param order: order obj
    :param items_ids: list of items ids
    :return:
    """

    for item_id in items_ids.split(','):
        item = Item.objects.get(id=item_id)
        order.items.add(item)
        order.total_price += item.price


def add_discount_to_order(order, discount_id):
    """
    Add discount to order (can add only one discount)
    :param order: order obj
    :param discount_id: id of discount
    :return:
    """

    discount = Discount.objects.get(id=discount_id)
    order.discounts.add(discount)
    try:
        stripe.Coupon.create(currency=discount.currency, duration='once', id=discount_id,
                             percent_off=discount.percent_off)
    except stripe.error.InvalidRequestError:
        pass


def add_taxes_to_order(order, taxes_ids):
    """
    Add taxes to order
    :param order: order obj
    :param taxes_ids: list of taxes ids
    :return:
    """

    for tax_id in taxes_ids.split(','):
        tax = Tax.objects.get(id=tax_id)
        order.taxes.add(tax)
        if tax.stripe_id == '':
            tax_stripe = stripe.TaxRate.create(display_name="Sales Tax", inclusive=False, percentage=tax.percentage)
            tax.stripe_id = tax_stripe.id
            tax.save()


def create_order(request):
    """
    Create a new order
    request.GET need contain `items_ids, discount_id, taxes_ids` fields
    example: https://example.com/create_order/?items_ids=1,2&discount_id=3&taxes_ids=1,2,3
    :param request:
    :return: Return an HttpResponse whose content is filled with the result
    """

    items_ids = request.GET.get('items_ids')
    discount_id = request.GET.get('discount_id')
    taxes_ids = request.GET.get('taxes_ids')

    order = Order.objects.create()

    add_items_to_order(order, items_ids)
    add_discount_to_order(order, discount_id)
    add_taxes_to_order(order, taxes_ids)

    order.save()

    return render(request, 'order.html', model_to_dict(order))


def order_check(request, order_id):
    """
    Get item by id
    :param request:
    :param order_id: id of order
    :return: Return an HttpResponse whose content is filled with the result
    """

    order = Order.objects.get(id=order_id)
    return render(request, 'order.html', model_to_dict(order))


def buy_order(request, order_id):
    """
    Create stripe session ID for order
    :param request:
    :param order_id: id of order
    :return: stripe session_id
    """

    order = Order.objects.get(id=order_id)
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': item.currency,
                        'product_data': {'name': item.name},
                        'unit_amount': item.price * 100,
                    },
                    'quantity': 1,
                    'tax_rates': [tax.stripe_id for tax in order.taxes.all()],
                } for item in order.items.all()
            ],
            discounts=[{'coupon': discount.id} for discount in order.discounts.all()],
            mode='payment',
            success_url='http://localhost:4242/success.html',
            cancel_url='http://localhost:4242/cancel.html',
        )
        return JsonResponse({'session_id': session.id})
    except stripe.error.InvalidRequestError as e:
        return HttpResponse(str(e))
