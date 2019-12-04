from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('newroom/', views.CreateRoomView.as_view(), name = 'create_room'),
    path('<str:room_name>/', views.room, name='room'),
]