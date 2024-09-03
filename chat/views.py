from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Room, Message

from django.http import JsonResponse

def check_room_exists(request):
    room_name = request.GET.get('room_name', '').strip()
    exists = Room.objects.filter(room_name__iexact=room_name).exists()
    return JsonResponse({'exists': exists})

def HomeView(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        room = request.POST.get("room", "").strip()
        your_room = request.POST.get("your_room", "").strip()
        room_password = request.POST.get("room_password", "").strip()

        if not username:
            messages.error(request, "Username is required.")
            return redirect('/')

        if your_room:
            room = your_room
            is_private = bool(room_password)

            existing_room = Room.objects.filter(room_name__iexact=room).first()
            if existing_room:
                messages.error(request, "Room already exists.")
                return redirect('/')

            new_room = Room.objects.create(room_name=room, status=is_private)
            if is_private:
                new_room.password = room_password
            new_room.save()

            return redirect("room", room_name=room, username=username)

        else:
            try:
                existing_room = Room.objects.filter(room_name__iexact=room).first()
                return redirect("room", room_name=room, username=username)
            except Room.DoesNotExist:
                messages.error(request, "Room does not exist.")
                return redirect('/')

    rooms = Room.objects.all()
    return render(request, "home.html", {"rooms": rooms})
    
def RoomView(request, room_name, username):
    try:
        have_room = Room.objects.filter(room_name__icontains=room_name).first()
    except Room.DoesNotExist:
        messages.error(request, "Room does not exist.")
        return redirect('home')

    room_status = have_room.status
    get_messages = Message.objects.filter(room=have_room)
    rooms = Room.objects.all()  
    public_rooms = Room.objects.filter(status=False)  

    if room_status:
        if request.method == "POST":
            room_password = request.POST.get("room_password")
            if room_password == have_room.password:
                context = {
                    "messages": get_messages,
                    "user": username,
                    "room_name": have_room.room_name,
                    "rooms": rooms,  
                    "room_status": False 
                }
                return render(request, "room.html", context)
            else:
                messages.error(request, "Incorrect password.")
                return redirect("room", room_name=room_name, username=username)
        else:
            context = {
                "messages": [],
                "user": username,
                "room_name": have_room.room_name,
                "rooms": rooms, 
                "room_status": True  
            }
            return render(request, "room.html", context)
    else:
        context = {
            "messages": get_messages,
            "user": username,
            "room_name": have_room.room_name,
            "rooms": rooms,  
            "room_status": False 
        }
        return render(request, "room.html", context)