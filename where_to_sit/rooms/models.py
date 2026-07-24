from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)  # например, «Переговорка 1» или «Room 201»
    capacity = models.PositiveIntegerField()  # вместимость

    def __str__(self):
        return f"{self.name} ({self.capacity} мест)"


class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    start = models.DateTimeField()
    end = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['room', 'start', 'end']),
            models.Index(fields=['user', 'start']),
        ]

    def clean(self):
        now = timezone.now()
        if self.start <= now:
            raise ValidationError("Время начала должно быть в будущем.")
        if self.end <= self.start:
            raise ValidationError("Время окончания должно быть строго позже времени начала.")
        duration_minutes = (self.end - self.start).total_seconds() / 60
        if duration_minutes > 180:  # 3 часа
            raise ValidationError("Одно бронирование не может длиться более 3 часов.")
        
    def save(self, *args, **kwargs):
        self.full_clean() # Запускаем валидацию полей
        super().save(*args, **kwargs)