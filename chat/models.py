from django.db import models

class Room(models.Model):
    room_name = models.CharField(max_length=55)
    #vai ser publica ou privada
    status = models.BooleanField(default=False)
    password = models.CharField(max_length=55, null=True, blank=True)

    def __str__(self):
        return self.room_name

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.CharField(max_length=55)
    message = models.TextField()

    def __str__(self):
        return f"{str(self.room)} - {self.sender}"