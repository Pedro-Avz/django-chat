from django.db import models
from django.utils.timezone import now
from datetime import timedelta

#problema com utc e time zone quando salvo as horas com now 
def adjusted_now():
    return now() - timedelta(hours=3)

class Room(models.Model):
    room_name = models.CharField(max_length=55)
    #um host para poder excluir a room
    host = models.CharField(max_length=55, null=False, default="Unknown")
    #vai ser publica ou privada
    status = models.BooleanField(default=False)
    password = models.CharField(max_length=55, null=True, blank=True)
    #membros dentro da sala
    active_users = models.JSONField(default=list, blank=True) 

    def __str__(self):
        return self.room_name

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.CharField(max_length=55)
    message = models.TextField()
    #colocar hora na mensagem
    created_at = models.DateTimeField(default=adjusted_now)
    

    def __str__(self):
        return f"{str(self.room)} - {self.sender}"