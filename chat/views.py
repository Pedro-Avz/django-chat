#models
from .models import Room, Message

#retornos , viewsets e serializer
from django.shortcuts import render, redirect

from django.contrib import messages

#responses
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

            new_room = Room.objects.create(room_name=room, status=is_private, host=username)
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

    have_room = Room.objects.filter(room_name__iexact=room_name).first()

    if not have_room:
        messages.error(request, "Room does not exist.")
        return redirect('/')

    room_status = have_room.status
    get_messages = Message.objects.filter(room=have_room)
    rooms = Room.objects.all()


    if not have_room and request.method == "POST":
        new_room = Room.objects.create(room_name=room_name, status=False, host=username)
        request.session['host'] = username  

    session_host = request.session.get('host')

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
                return redirect("room", room_name=room_name, username=username)
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

    # Verificação de Deleção (opcional, pode ser em outra view)
    if request.method == 'DELETE' and session_host and session_host == have_room.host:
        # Chame a view de deleção (RoomDeleteView) para deletar a sala
        return redirect('delete-room', room_name=room_name)  # Substitua 'delete-room' pelo nome da sua URL de deleção

    # Mensagem de erro para deleção não autorizada
    messages.error(request, "You are not authorized to delete this room")
    return redirect("room", room_name=room_name, username=username)