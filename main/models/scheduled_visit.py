from django.contrib.auth.models import User
from django.db import models


class ScheduledVisit(models.Model):
    check_in = models.DateField()
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_scheduled_visits')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_visits')
    location = models.ForeignKey('main.Location', on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = "Ruta"
        verbose_name_plural = "Rutas"
        unique_together = [('check_in', 'user', 'supervisor', 'location')]

    def get_status(self):
        from main.models import Visit
        visit = Visit.objects.filter(user=self.user, check_in__date=self.check_in, location=self.location).first()
        if visit is None:
            return 'Pendiente'
        else:
            if visit.check_out is not None:
                return 'Finalizado'
            else:
                return "Iniciado"
