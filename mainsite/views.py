from django.shortcuts import render
from django.utils.safestring import mark_safe
import json


def index(request):
    return render(request, 'mainsite/index.html', {})

    
def room(request, room_name):
    return render(request, 'mainsite/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })
