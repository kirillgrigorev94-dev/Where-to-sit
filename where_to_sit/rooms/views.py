from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Room, Booking
from .serializers import RoomSerializer, BookingSerializer
from django.db.models import Q
from django.utils import timezone

class RoomListView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # можно включить DRF-пагинацию, если требуется


class RoomFreeListView(generics.ListAPIView):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        start_str = self.request.query_params.get('start')
        end_str = self.request.query_params.get('end')
        if not start_str or not end_str:
            return Room.objects.none()

        from django.utils.dateparse import parse_datetime
        start = parse_datetime(start_str)
        end = parse_datetime(end_str)
        if not start or not end:
            return Room.objects.none()

        # Комнаты, у которых нет пересечений в указанный интервал
        occupied_rooms = Booking.objects.filter(
            start__lt=end,
            end__gt=start,
        ).values_list('room_id', flat=True)

        return Room.objects.exclude(id__in=occupied_rooms)


class BookingCreateView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]


class MyBookingsListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


class BookingDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Разрешаем удалять только свои бронирования
        return Booking.objects.filter(user=self.request.user)