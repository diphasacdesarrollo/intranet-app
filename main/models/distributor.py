from django.db import models


class Distributor(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Distribuidor"
        verbose_name_plural = "Distribuidores"

    def __str__(self):
        return self.name
