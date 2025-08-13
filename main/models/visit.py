import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Visit(models.Model):
    check_in = models.DateTimeField()
    check_out = models.DateTimeField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=15, decimal_places=12)
    longitude = models.DecimalField(max_digits=15, decimal_places=12)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.ForeignKey('main.Location', on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = "Visita"
        verbose_name_plural = "Visitas"
        indexes = [
            models.Index(fields=['user', 'check_in', 'location']),
        ]

    @property
    def check_in_lima_time(self):
        return self.check_in - datetime.timedelta(hours=5)

    @property
    def check_out_lima_time(self):
        return self.check_out - datetime.timedelta(hours=5)

    @property
    def duration(self):
        """
        Returns the duration as a datetime object starting from 1970-01-01 00:00:00.
        """
        from datetime import datetime
        if self.check_out:
            duration = self.check_out - self.check_in
        else:
            duration = timezone.now() - self.check_in

        # Convert timedelta to a datetime object
        base_datetime = datetime(1970, 1, 1)  # Arbitrary starting point
        duration_as_datetime = base_datetime + duration
        return duration_as_datetime

    def get_total_quantity(self):
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

    def get_distinct_products_count(self):
        if self.items.exists():
            return self.items.values('product').distinct().count()
        return 0

    def get_google_maps_link(self) -> str:
        """
        Generates a Google Maps link for a given latitude and longitude.

        :param latitude: The latitude of the location.
        :param longitude: The longitude of the location.
        :return: A Google Maps URL pointing to the given coordinates.
        """
        return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
