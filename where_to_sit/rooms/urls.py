from django.urls import path, include
from .views import RoomListView, RoomFreeListView, BookingCreateView, MyBookingsListView, BookingDeleteView

urlpatterns = [
    path('rooms/', RoomListView.as_view(), name='room-list'),
    path('rooms/free/', RoomFreeListView.as_view(), name='room-free-list'),
    path('bookings/', BookingCreateView.as_view(), name='booking-create'),
    path('bookings/my/', MyBookingsListView.as_view(), name='my-bookings'),
    path('bookings/<int:pk>/', BookingDeleteView.as_view(), name='booking-delete'),
]