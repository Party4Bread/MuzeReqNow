from django.shortcuts import render,redirect
from django.utils.safestring import mark_safe
import json
import base64
from .models import RoomLists
import random

def index(request):
    return render(request, 'mainsite/index.html', {})

    
def room(request, room_name):
    if RoomLists.objects.filter(room_number=room_name).first() is None:
        return redirect(index)

    if request.session.get('owned_rooms',False):
        if room_name in request.session['owned_rooms']:
            return render(request, 'mainsite/admin.html', {
                'room_name_json': mark_safe(json.dumps(room_name)),
                'room_name':room_name
            }) 
    return render(request, 'mainsite/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name)),
        'room_name':room_name
    })

def create_room(req):
    n=random.randint(0,62**3)
    charset = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    chs = []
    while n > 0:
        r = n % 62
        n //= 62
        chs.append(charset[r])

    if len(chs) > 0:
        chs.reverse()
    else:
        chs.append("0")

    s = "".join(chs)
    s = charset[0] * max(4 - len(s), 0) + s
    RoomLists(room_number=s).save()
    if not req.session.get('owned_rooms', False):
        req.session['owned_rooms']=[]
    req.session['owned_rooms'].append(s)
    req.session.modified = True
    print(req.session['owned_rooms'])
    return redirect(room,room_name=s)