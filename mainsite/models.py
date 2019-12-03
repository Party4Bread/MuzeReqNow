from django.db import models

class MusicFiles(models.Model):
    url = models.TextField()
    origin_checksum = models.TextField()
    checksum = models.TextField()
    path = models.TextField()

class RoomLists(models.Model):
    room_number=models.TextField(unique=True)
    created_time=models.DateTimeField(auto_now=True)

class PlayLists(models.Model):
    room_number=models.ForeignKey(RoomLists,models.CASCADE,null=False)
    music=models.ForeignKey(MusicFiles,models.CASCADE,null=True)
    created_time=models.DateTimeField(auto_now=True)
