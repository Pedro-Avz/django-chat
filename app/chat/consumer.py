import json
from channels.generic.websocket import  AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message


# alguns metodos são especificos, e destinados nao posso mudar
class ChatConsumer(AsyncWebsocketConsumer):


    async def connect(self):

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.username = self.scope['url_route']['kwargs']['username']
        
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        group_name = f"room_{self.room_name}"
        await self.channel_layer.group_add(group_name, self.channel_name)
        await self.channel_layer.group_add("rooms_group", self.channel_name)
        room = await database_sync_to_async(Room.objects.get)(room_name=self.room_name)
        if self.username.lower() not in [user.lower() for user in room.active_users]:
            room.active_users.append(self.username)
            await database_sync_to_async(room.save)()

        
        await self.accept()


    async def disconnect(self, code):

        room_name = self.scope['url_route']['kwargs']['room_name']
        username = self.scope['url_route']['kwargs']['username']
        
        print(f"userername {username} saiu da sala {room_name}")

        room = await database_sync_to_async(Room.objects.get)(room_name=room_name)
        room.active_users = [user for user in room.active_users if user.lower() != username.lower()]
        
        print(f"estao na sala: {room.active_users}")
        await database_sync_to_async(room.save)()

        await self.channel_layer.group_discard(f"room_{room_name}", self.channel_name)
        await self.close(code)

    async def receive(self, text_data):

        print("mensagem recebida")
        data_json = json.loads(text_data)
        print("mensagem: ",data_json)

        event = {
            "type": "send_message",
            "message": data_json
        }

        await self.channel_layer.group_send(self.room_name, event)

    async def send_message(self, event):
        
        data=event["message"]
        await self.create_message(data = data)

        response = {
            "sender": data["sender"],
            "message": data["message"]
        }
        
        await self.send(text_data=json.dumps(
            {"message": response})
        )

    @database_sync_to_async
    def create_message(self, data):

        get_room = Room.objects.get(room_name=data['room_name'])
        if not Message.objects.filter(message=data['message'], sender=data['sender']).exists():
            new_message = Message.objects.create(
                room = get_room,
                sender = data['sender'],
                message = data['message']
            )

    async def room_deleted(self, event):
        #enviar pro front q a sala foi deletada
        await self.send(text_data=json.dumps({
            "action": "room_deleted",
            "message": event["message"]
        }))

    async def room_create(self, event):
        #enviar pro front q a sala foi criada
        await self.send(text_data=json.dumps({
            "action": "room_create",
            "room_name": event["room_name"]
        }))