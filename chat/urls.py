from django.urls import path
from .views import HomeView, RoomView, check_room_exists

urlpatterns = [
    path("" , HomeView, name="login"),
    path("<str:room_name>/<str:username>/", RoomView, name="room"),
    path('check-room-exists/', check_room_exists, name='check_room_exists'),
]