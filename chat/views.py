from django.shortcuts import render, redirect
from .models import Room, Message

def HomeView(request):

    if request.method == "POST":
        username = request.POST["username"]
        room = request.POST["room"]

        try:
            #usar icontains para conseguir abrir a sala independente de letra maiuscula ou minuscula
            #evitando criar novas salas 
            have_room = Room.objects.get(room_name__icontains=room)
        
        except Room.DoesNotExist:
            new_room = Room.objects.create(room_name=room)
        return redirect("room", room_name=room, username=username)
    return render(request,  "home.html")

def RoomView(request, room_name, username):

    have_room = Room.objects.get(room_name__icontains=room_name)
    get_messages = Message.objects.filter(room=have_room)
    context = {
        "messages": get_messages,
        "user": username,
        "room_name" : have_room.room_name

    }
    return render(request,  "room.html", context)