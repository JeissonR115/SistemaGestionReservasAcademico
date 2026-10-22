from django.core.validators import MinValueValidator
from django.db import models


class Space(models.Model):
    name = models.CharField(max_length=120, unique=True)
    space_type = models.CharField(max_length=80)
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    is_active = models.BooleanField(default=True)
    reservation_version = models.PositiveBigIntegerField(default=0, editable=False)

    class Meta:
        ordering = ('name', 'id')

    def __str__(self):
        return self.name
