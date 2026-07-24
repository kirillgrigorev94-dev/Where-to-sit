
import pytest
from django.utils import timezone
from datetime import timedelta
from rooms.models import Room, Booking
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="password")

@pytest.fixture
def room():
    return Room.objects.create(name="Room A", capacity=10)

@pytest.mark.django_db
def test_booking_overlap_rejected(user, room):
    now = timezone.now() + timedelta(hours=1)
    b1 = Booking.objects.create(room=room, user=user, start=now, end=now + timedelta(hours=1))

    # Пытаемся забронировать ту же комнату на пересекающееся время
    from rest_framework.test import APIClient
    client = APIClient()
    client.force_authenticate(user=user)

    data = {
        "room": room.id,
        "start": (now + timedelta(minutes=30)).isoformat(),
        "end": (now + timedelta(hours=2)).isoformat(),
    }
    resp = client.post("/api/bookings/", data, format="json")
    assert resp.status_code == 400
    assert "пересечение" in str(resp.data).lower()
    
@pytest.mark.django_db
def test_booking_duration_limit_exceeded(user, room):
    now = timezone.now() + timedelta(hours=1)
    
    from rest_framework.test import APIClient
    client = APIClient()
    client.force_authenticate(user=user)

    # Пытаемся забронировать на 4 часа (лимит — 3 часа)
    data = {
        "room": room.id,
        "start": now.isoformat(),
        "end": (now + timedelta(hours=4)).isoformat(),
    }
    resp = client.post("/api/bookings/", data, format="json")
    
    assert resp.status_code == 400
    assert "лимит" in str(resp.data).lower() or "3 часа" in str(resp.data).lower()
    

@pytest.mark.django_db
def test_user_daily_limit_exceeded(user, room):
    now = timezone.now() + timedelta(hours=1)
    
    from rest_framework.test import APIClient
    client = APIClient()
    client.force_authenticate(user=user)

    # 1. Создаём первое бронирование на 3 часа
    Booking.objects.create(
        room=room,
        user=user,
        start=now,
        end=now + timedelta(hours=3)
    )

    # 2. Пытаемся создать второе бронирование на 2 часа в тот же день
    data = {
        "room": room.id,
        "start": (now + timedelta(hours=3)).isoformat(),
        "end": (now + timedelta(hours=5)).isoformat(),
    }
    resp = client.post("/api/bookings/", data, format="json")
    
    assert resp.status_code == 400
    assert "лимит" in str(resp.data).lower() or "4 часа" in str(resp.data).lower()
    

@pytest.mark.django_db
def test_booking_in_past_rejected(user, room):
    past_time = timezone.now() - timedelta(hours=1)
    
    from rest_framework.test import APIClient
    client = APIClient()
    client.force_authenticate(user=user)

    data = {
        "room": room.id,
        "start": past_time.isoformat(),
        "end": (past_time + timedelta(hours=1)).isoformat(),
    }
    resp = client.post("/api/bookings/", data, format="json")
    
    assert resp.status_code == 400
    assert "прошлое" in str(resp.data).lower() or "в прошлом" in str(resp.data).lower()