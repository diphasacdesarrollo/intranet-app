from django.db import models


class VisitItem(models.Model):
    visit = models.ForeignKey('main.Visit', on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey('main.Product', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    distributor = models.ForeignKey('main.Distributor', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = "Item de visita"
        verbose_name_plural = "Items de visita"
        unique_together = [('visit', 'product', 'distributor')]

    @classmethod
    def export_headers(cls):
        return ['Fecha de visita', 'Producto', 'Presentación', 'Cantidad', 'Precio unitario', 'Distribuidor',
                'Vendedor']

    @property
    def subtotal(self):
        return self.quantity * self.unit_price