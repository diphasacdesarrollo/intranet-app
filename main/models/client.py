import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Client(models.Model):
    category = models.ForeignKey('main.ClientCategory', on_delete=models.SET_NULL, verbose_name="Categoría", null=True,
                                 blank=True)
    name = models.CharField(max_length=200, verbose_name="Nombre")
    ruc = models.CharField(max_length=13, unique=True, verbose_name="RUC", null=True, blank=True)
    account_manager = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name="Vendedor",
                                        null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
