from django.urls import path
from .views import HomeView, RoomView, check_room_exists, RoomDeleteView, check_username_in_room



urlpatterns = [
    path("" , HomeView, name="login"),
    path("<str:room_name>/<str:username>/", RoomView, name="room"),
    path('check-room-exists/', check_room_exists, name='check_room_exists'),
    path('delete-room/', RoomDeleteView, name='delete-room'),
    path('check-username-in-room/', check_username_in_room, name='check-username-in-room'),
]


