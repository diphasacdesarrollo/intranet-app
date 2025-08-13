from django.db import models


class ProductPrice(models.Model):
    valid_from = models.DateField()
    valid_to = models.DateField()
    product = models.ForeignKey('main.Product', on_delete=models.CASCADE)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    quantity_a = models.IntegerField(null=True, blank=True)
    commission_a = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    quantity_b = models.IntegerField(null=True, blank=True)
    commission_b = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_monthly_product_prices(cls, date) -> models.QuerySet:
        return cls.objects.filter(
            valid_from__month=date.month,
            valid_from__year=date.year,
            quantity_a__gt=0
        )

    class Meta:
        verbose_name = "Precio de producto"
        verbose_name_plural = "Precios de productos"
        unique_together = [('valid_from', 'valid_to', 'product')]
