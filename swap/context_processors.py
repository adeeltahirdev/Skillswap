def notification_counts(request):
    if not request.user.is_authenticated:
        return {}

    from .models import Notification, SwapRequest, Message

    return {
        'unread_swap_requests': SwapRequest.objects.filter(recipient=request.user, status='pending').count(),
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
        'unread_messages': Message.objects.filter(recipient=request.user, is_read=False).count(),
    }
