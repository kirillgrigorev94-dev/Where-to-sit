from rest_framework import serializers
from .models import Room, Booking
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from django.db.models.fields import DurationField

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
            raise serializers.ValidationError("Нельзя бронировать время, которое уже в прошлом.")
        if end <= start:
            raise serializers.ValidationError("Время окончания должно быть строго позже времени начала.")

        # 2. Длительность <= 3 часа
        # Объявляем duration здесь — это ключевой объект timedelta
        duration = end - start
        if duration > timedelta(hours=3):
            raise serializers.ValidationError("Превышен лимит длительности: одно бронирование не более 3 часов.")

        # 3. Проверка пересечений с другими бронированиями этой комнаты
        overlapping = Booking.objects.filter(
            room=room,
            start__lt=end,
            end__gt=start,
        ).exclude(pk=self.instance.pk if self.instance else None)
        if overlapping.exists():
            raise serializers.ValidationError("Комната уже забронирована на это время (пересечение).")

        # 4. Суммарное время бронирований пользователя за календарный день
        day_start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        existing_bookings = Booking.objects.filter(
            user=user,
            start__gte=day_start,
            start__lt=day_end,
        )

        # Агрегация с явным указанием типа
        total_duration_existing = existing_bookings.aggregate(
            total=Coalesce(
                Sum(F('end') - F('start')), 
                timedelta(0), 
                output_field=DurationField()
            )
        )['total']

        # ГАРАНТИРУЕМ, что переменная не None. Это уберёт подчёркивание и защитит от краша.
        if total_duration_existing is None:
            total_duration_existing = timedelta(0)

        # Теперь .total_seconds() безопасен
        total_minutes = (total_duration_existing.total_seconds() + duration.total_seconds()) / 60 # type: ignore
    
        if total_minutes > 240:
            raise serializers.ValidationError(
                "Превышен дневной лимит пользователя: суммарно не более 4 часов в день."
            )

        return data