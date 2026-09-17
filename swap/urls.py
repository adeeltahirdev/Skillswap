from django.urls import path
from . import views

urlpatterns = [
    path('swaps/', views.requests, name='requests'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('swaps/active/', views.active_swaps, name='active_swaps'),
    path('swaps/completed/', views.completed_swaps, name='completed_swaps'),
    path('swaps/<int:pk>/', views.request_detail, name='request_detail'),
    path('swaps/request/<int:skill_id>/', views.send_swap_request, name='send_swap_request'),
    path('swaps/<int:pk>/action/', views.swap_action, name='swap_action'),
    path('swaps/<int:pk>/review/', views.submit_review, name='submit_review'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('messages/', views.inbox, name='inbox'),
    path('messages/<str:username>/', views.conversation, name='conversation'),
]
