from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from spaces.models import Space


class Reservation(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        APPROVED = 'approved', 'Aprobada'
        REJECTED = 'rejected', 'Rechazada'
        CANCELLED = 'cancelled', 'Cancelada'

    space = models.ForeignKey(
        Space,
        on_delete=models.PROTECT,
        related_name='reservations',
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='reservations',
    )
    purpose = models.CharField(max_length=500)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ('start_at', 'id')
        constraints = [
            models.CheckConstraint(
                condition=Q(start_at__lt=F('end_at')),
                name='reservation_start_before_end',
            ),
            models.CheckConstraint(
                condition=Q(
                    status__in=('pending', 'approved', 'rejected', 'cancelled')
                ),
                name='reservation_status_is_valid',
            ),
        ]
        indexes = [
            models.Index(
                fields=('space', 'status', 'start_at', 'end_at'),
                name='reservation_conflict_idx',
            ),
        ]

    def __str__(self):
        return f'{self.space} ({self.start_at} - {self.end_at})'


class ReservationLog(models.Model):
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.PROTECT,
        related_name='history',
    )
    status = models.CharField(max_length=10, choices=Reservation.Status.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='reservation_changes',
    )
    changed_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ('changed_at', 'id')
