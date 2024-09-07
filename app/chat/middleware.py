import re
from django.shortcuts import redirect
from django.contrib import messages
from .models import Room

class RoomAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        pattern = r'^/(?P<room_name>[a-zA-Z0-9-_]+)/(?P<username>[a-zA-Z0-9-_]+)/$'
        path = request.path_info
        match = re.match(pattern, path)
        
        if match:
            room_name = match.group('room_name')
            username = match.group('username')
            if not request.session.get(f'room_{room_name}_user') == username:
                room = Room.objects.filter(room_name__iexact=room_name).first()
                
                if room:
                    active_users_lower = [user.lower() for user in room.active_users]
                    username_lower = username.lower()

                    if username_lower in active_users_lower:
                        messages.error(request, "Username already taken in this room.")
                        return redirect('/')
                    else:
                        request.session[f'room_{room_name}_user'] = username
                else:
                    messages.error(request, "Room does not exist.")
                    return redirect('/')
        return self.get_response(request)
