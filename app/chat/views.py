#models
from .models import Room, Message

#renders
from django.shortcuts import render, redirect

#responses
from django.http import JsonResponse
from django.contrib import messages
import json
#channels websocket
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def check_room_exists(request):
    room_name = request.GET.get('room_name', '').strip()
    exists = Room.objects.filter(room_name__iexact=room_name).exists()
    return JsonResponse({'exists': exists})

def check_username_in_room(request):
    username = request.GET.get('username', '').strip().lower()
    room_name = request.GET.get('room_name', '').strip()

    try:
        room = Room.objects.get(room_name__iexact=room_name)
        username_exists = username in [user.lower() for user in room.active_users]
        return JsonResponse({'usernameExists': username_exists})
    except Room.DoesNotExist:
        return JsonResponse({'usernameExists': False})

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

            if room.lower() == "admin":
                messages.error(request, "You cannot use 'admin' as a room name.")
                return JsonResponse({"message" : "You cannot use 'admin' as a room name." , "status" : 400})

            existing_room = Room.objects.filter(room_name__iexact=room).first()
            if existing_room:
                messages.error(request, "Room already exists.")
                return redirect('/')

            new_room = Room.objects.create(room_name=room, status=is_private, host=username)
            if is_private:
                new_room.password = room_password
            new_room.save()

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"rooms_group",
                {
                    "type": "room_create",
                    "room_name": new_room.room_name
                }
            )
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
    have_room = Room.objects.filter(room_name__iexact=room_name).first()

    if not have_room:
        messages.error(request, "Room does not exist.")
        return redirect('/')

    active_users_lower = [user.lower() for user in have_room.active_users]
    have_room.active_users.append(username)
    have_room.save()


    room_status = have_room.status
    get_messages = Message.objects.filter(room=have_room)
    rooms = Room.objects.all()

    session_host = request.session.get('host')
    if not session_host:
        request.session['host'] = username
        session_host = username

    if room_status:
        if request.method == "POST":
            room_password = request.POST.get("room_password")
            if room_password == have_room.password:
                context = {
                    "messages": get_messages,
                    "user": username,
                    "room_name": have_room.room_name,
                    "rooms": rooms,
                    "room_status": False,
                    "room_host": have_room.host,
                }
                return render(request, "room.html", context)
            else:
                messages.error(request, "Incorrect password.")
                return redirect("/")
        else:
            context = {
                "messages": [],
                "user": username,
                "room_name": have_room.room_name,
                "rooms": rooms,
                "room_status": True,
                "room_host": have_room.host,
            }
            return render(request, "room.html", context)
    else:
        context = {
            "messages": get_messages,
            "user": username,
            "room_name": have_room.room_name,
            "rooms": rooms,
            "room_status": False,
            "room_host": have_room.host,
        }
        return render(request, "room.html", context)

def RoomDeleteView(request):
    #print("entrou na view....")
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            #print("data", data)
            room_name = data.get('room')
            host = data.get('host')
        except (ValueError, KeyError):
            return JsonResponse({'message': 'Invalid data', 'status': 400})

        if not room_name or not host:
            return JsonResponse({'message': 'Missing parameters', 'status': 400})

        delete_room = Room.objects.filter(room_name=room_name, host=host).first()

        if not delete_room:
            return JsonResponse({'message': 'Room or host not found', 'status': 404})
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"room_{room_name}",
            {
                "type": "room_deleted",
                "message": "Room has been deleted by the host."
            }
        )

        delete_room.delete()
        return JsonResponse({'message': 'Room deleted successfully'})

    return JsonResponse({'message': 'Method not allowed'}, status=405)