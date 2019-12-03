from asgiref.sync import async_to_sync,sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
import youtube_dl
import asyncio
import uuid
import pathlib
from .models import MusicFiles,PlayLists,RoomLists

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        #await self.send_json()


    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        msg_type = text_data_json['msgType']
        if msg_type == "request_song":
            path = await self.download_music(message)

            await self.send(text_data=json.dumps({
                'type':"request_result",
                'message': path is not None
            }))

            if path is not None:                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'add_song',
                        'message': path
                    }
                )
        else:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_msg',
                    'message': message
                }
            )

    async def add_song(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type':"add_song",
            'message': message
        }))

    async def chat_msg(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type':"chat_msg",
            'message': message
        }))

    @database_sync_to_async
    def get_music(self,url):
        return MusicFiles.objects.filter(url=url).first()
        
    @database_sync_to_async
    def save_music(self,url,path):
        musicFile=MusicFiles(url=url,path=path)
        musicFile.save()

    @database_sync_to_async
    def add_music(self,room_num,url):
        musicFile=PlayLists(room_number=RoomLists.objects.get(room_number=room_num),music=MusicFiles.objects.get(url=url))
        musicFile.save()
    
    
    # Return File path or None
    async def download_music(self, url)->str:
        file = await self.get_music(url)
        if file is None:
            q = []
            newfoldername=str(uuid.uuid4())
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'opus',
                }],
                'writeinfojson':True,
                'writethumbnail':True,
                'progress_hooks':[q.append],
                'outtmpl':"downloadedmusics/"+newfoldername+"/"+'dlfile.%(ext)s'
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                for p in q:
                    if p["status"]=="finished":
                        musicFile=MusicFiles(url=url,path="downloadedmusics/"+newfoldername)
                        await self.save_music(url,"downloadedmusics/"+newfoldername)
                        return musicFile.path
                    elif p["status"]=="error":
                        return None
        else:
            return file.path