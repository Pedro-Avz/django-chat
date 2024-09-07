from django.urls import path
from .consumer import ChatConsumer

wsPattern = [
    path("ws/messages/<str:room_name>/<str:username>/" , ChatConsumer.as_asgi()),
]