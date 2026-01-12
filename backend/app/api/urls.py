"""
API URL configuration.
"""
from django.urls import path
from . import views

urlpatterns = [
    # 注意：更具体的路由必须放在前面，避免被通用路由拦截
    path('rooms/<str:room_id>/start', views.RoomStartView.as_view(), name='room-start'),
    path('rooms/<str:room_id>/vote', views.RoomVoteView.as_view(), name='room-vote'),
    path('rooms/<str:room_id>/reset', views.RoomResetView.as_view(), name='room-reset'),
    path('rooms/<str:room_id>', views.RoomDetailView.as_view(), name='room-detail'),
    path('rooms', views.RoomCreateView.as_view(), name='room-create'),
]
