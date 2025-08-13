import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class ClientCategory(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    apply_sales_commission = models.BooleanField(default=False, verbose_name="Aplicar comisión de ventas")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización", null=True, blank=True)

    class Meta:
        verbose_name = "Categoría de cliente"
        verbose_name_plural = "Categorías de clientes"

    def __str__(self):
        return self.name
