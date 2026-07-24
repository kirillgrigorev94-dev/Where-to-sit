from rest_framework import serializers
from .models import Room, Booking
from django.utils import timezone
from django.db.models import Sum, F
from django.db.models.functions import Coalesce

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'capacity']


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Booking
        fields = ['id', 'room', 'user', 'start', 'end']
        read_only_fields = ['user']

    def validate(self, data):
        room = data['room']
        start = data['start']
        end = data['end']
        user = data['user']
        now = timezone.now()

        # 1. Время в будущем, end > start
        if start <= now:
            raise serializers.ValidationError("Время начала должно быть в будущем.")
        if end <= start:
            raise serializers.ValidationError("Время окончания должно быть строго позже времени начала.")

        # 2. Длительность <= 3 часа
        duration_minutes = (end - start).total_seconds() / 60
        if duration_minutes > 180:
            raise serializers.ValidationError("Одно бронирование не может длиться более 3 часов.")

        # 3. Проверка пересечений с другими бронированиями этой комнаты
        overlapping = Booking.objects.filter(
            room=room,
            start__lt=end,
            end__gt=start,
        ).exclude(pk=self.instance.pk if self.instance else None)
        if overlapping.exists():
            raise serializers.ValidationError("Комната уже забронирована на это время (пересечение).")

        # 4. Суммарное время бронирований пользователя за календарный день (00:00–23:59)
        day_start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start.replace(hour=23, minute=59, second=59, microsecond=999999)

        existing_bookings = Booking.objects.filter(
            user=user,
            start__gte=day_start,
            start__lte=day_end,
        )

        total_minutes_existing = existing_bookings.aggregate(
            total=Coalesce(Sum(F('end') - F('start')), 0)
        )['total']
        if total_minutes_existing is None:
            total_minutes_existing = 0

        # Конвертируем timedelta в минуты
        if isinstance(total_minutes_existing, int | float):
            # на случай, если агрегация вернула число (редко, но бывает в тестах)
            pass
        else:
            total_minutes_existing = total_minutes_existing.total_seconds() / 60 if hasattr(total_minutes_existing, 'total_seconds') else 0

        new_duration_minutes = duration_minutes
        if (total_minutes_existing + new_duration_minutes) > 240:  # 4 часа = 240 минут
            raise serializers.ValidationError(
                "Суммарное время ваших бронирований в течение дня не может превышать 4 часов."
            )

        return data