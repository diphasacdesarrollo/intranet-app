from .attendance import Attendance
from .client import Client
from .client_category import ClientCategory
from .distributor import Distributor
from .location import Location
from .product import Product
from .product_price import ProductPrice
from .scheduled_visit import ScheduledVisit
from .supervised_user import SupervisedUser
from .visit import Visit
from .visit_item import VisitItem

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Prefetch, QuerySet


def get_clients_data():
    clients = Client.objects.prefetch_related(
        Prefetch('locations', queryset=Location.objects.only('id', 'address'))
    ).values('id', 'name', 'ruc', 'locations__id', 'locations__address')

    client_dict = {}
    for client in clients:
        client_id = client['id']
        if client_id not in client_dict:
            if client["ruc"] is None:
                client_dict[client_id] = {
                    "name": client["name"],
                    "ruc": '',
                    "locations": []
                }
            else:
                client_dict[client_id] = {
                    "name": client["name"],
                    "ruc": client["ruc"],
                    "locations": []
                }
        if client["locations__id"]:
            client_dict[client_id]["locations"].append({
                "id": client["locations__id"],
                "address": client["locations__address"]
            })

    return client_dict


def get_progress(user: User, date) -> QuerySet:
    # First get all product prices with quantity a not null and greater than 0 in the month of the given date
    product_prices = ProductPrice.get_monthly_product_prices(date)

    # Now for every product price, get the product total quantity sold by the user in the month of the given date
    # only if the unit price is great than the product unit price
    for product_price in product_prices:
        visit_items = VisitItem.objects.filter(
            visit__user=user,
            visit__check_in__month=date.month,
            visit__check_in__year=date.year,
            product=product_price.product,
        )
        valid_visit_items = visit_items.filter(
            unit_price__gte=product_price.unit_price
        )
        total_quantity = valid_visit_items.aggregate(total=models.Sum('quantity'))['total'] or 0

        product_price.total_quantity = total_quantity

        commission = 0
        if total_quantity >= product_price.quantity_a:
            commission = product_price.commission_a * total_quantity
        product_price.progress_a = min(total_quantity/product_price.quantity_a, 1)

        if product_price.quantity_b is not None:
            if total_quantity >= product_price.quantity_b:
                commission = product_price.commission_b * total_quantity
            product_price.progress_b = min(total_quantity/product_price.quantity_b, 1)
        else:
            product_price.progress_b = None

        product_price.commission = commission
        product_price.visit_items = visit_items

    return product_prices
