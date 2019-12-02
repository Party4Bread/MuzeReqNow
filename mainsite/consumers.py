from channels.generic.websocket import WebsocketConsumer
import json
from channels.db import database_sync_to_async

async def connect(self):
    self.username = await database_sync_to_async(self.get_name)()
    
class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        self.send(text_data=json.dumps({
            'message': message
        }))