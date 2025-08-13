from django.db import models


class Location(models.Model):
    address = models.CharField(max_length=250, verbose_name="Dirección")
    latitude = models.DecimalField(max_digits=15, decimal_places=12, verbose_name="Latitud", null=True, blank=True)
    longitude = models.DecimalField(max_digits=15, decimal_places=12, verbose_name="Longitud", null=True, blank=True)
    client = models.ForeignKey('main.Client', on_delete=models.CASCADE, verbose_name="Cliente", related_name="locations")
    googlemaps_place_id = models.CharField(max_length=250, verbose_name="ID de lugar de Google Maps", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización", null=True, blank=True)

    class Meta:
        verbose_name = "Local"
        verbose_name_plural = "Locales"

    def __str__(self):
        return self.address.replace(', Peru', '')
