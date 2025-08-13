import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    check_in = models.DateTimeField()
    latitude_check_in = models.DecimalField(max_digits=15, decimal_places=12, verbose_name="Latitud Check In")
    longitude_check_in = models.DecimalField(max_digits=15, decimal_places=12, verbose_name="Longitud Check In")
    check_out = models.DateTimeField(null=True, blank=True)
    latitude_check_out = models.DecimalField(max_digits=15, decimal_places=12, verbose_name="Latitud Check Out",
                                             null=True, blank=True)
    longitude_check_out = models.DecimalField(max_digits=15, decimal_places=12, verbose_name="Longitud Check Out",
                                              null=True, blank=True)
    check_in_photo = models.ImageField(upload_to='attendance_photos', null=True, blank=True)
    check_out_photo = models.ImageField(upload_to='attendance_photos', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"

    @property
    def check_in_lima_time(self):
        return self.check_in - datetime.timedelta(hours=5)

    @property
    def check_out_lima_time(self):
        return self.check_out - datetime.timedelta(hours=5)

    def get_google_maps_link_check_in(self) -> str:
        return f"https://www.google.com/maps?q={self.latitude_check_in},{self.longitude_check_in}"

    def get_google_maps_link_check_out(self) -> str:
        return f"https://www.google.com/maps?q={self.latitude_check_out},{self.longitude_check_out}"

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

    def get_visits_count(self):
        from .visit import Visit
        visits =  Visit.objects.filter(user=self.user, check_in__date=self.check_in.date())
        if self.check_out:
            visits = visits.filter(check_out__date=self.check_out.date())
        return visits.count()