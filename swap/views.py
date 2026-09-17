from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Avg
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from skills.models import Skill
from .models import SwapRequest, Review, Activity, Notification, Message

def create_notification(user, title, message, link=''):
    Notification.objects.create(user=user, title=title, message=message, link=link)

def create_activity(user, title, description, icon='bi bi-arrow-left-right'):
    Activity.objects.create(user=user, title=title, description=description, icon=icon)

@login_required
def requests(request):
    incoming_requests = SwapRequest.objects.filter(recipient=request.user).select_related('requester', 'offered_skill', 'requested_skill').order_by('-created_at')
    outgoing_requests = SwapRequest.objects.filter(requester=request.user).select_related('recipient', 'offered_skill', 'requested_skill').order_by('-created_at')
    return render(request, 'swap/requests.html', {'incoming_requests': incoming_requests, 'outgoing_requests': outgoing_requests})

@login_required
def dashboard(request):
    user_swaps = SwapRequest.objects.filter(Q(requester=request.user) | Q(recipient=request.user))
    context = {
        'active_count': user_swaps.filter(status='accepted').count(),
        'completed_count': user_swaps.filter(status='completed').count(),
        'pending_count': user_swaps.filter(status='pending').count(),
        'recent_activity': Activity.objects.filter(user=request.user).order_by('-created_at')[:8],
    }
    return render(request, 'swap/dashboard.html', context)

@login_required
def request_detail(request, pk):
    swap_request = get_object_or_404(SwapRequest.objects.select_related('requester__profile', 'recipient__profile', 'offered_skill', 'requested_skill'), pk=pk)
    if request.user not in [swap_request.requester, swap_request.recipient]:
        return HttpResponseForbidden('You do not have permission to view this swap request.')
    can_review = swap_request.status == 'completed' and not Review.objects.filter(swap=swap_request, reviewer=request.user).exists()
    other_user = swap_request.other_user(request.user)
    return render(request, 'swap/request_detail.html', {'swap_request': swap_request, 'can_review': can_review, 'other_user': other_user})

@login_required
def send_swap_request(request, skill_id):
    requested_skill = get_object_or_404(Skill, pk=skill_id)
    if requested_skill.user == request.user:
        messages.error(request, 'You cannot request a swap for your own skill.')
        return redirect('skill_detail', pk=skill_id)
    offered_skills = Skill.objects.filter(user=request.user, skill_type='offer')
    if request.method == 'POST':
        offered_skill = get_object_or_404(offered_skills, pk=request.POST.get('offered_skill'))
        if SwapRequest.objects.filter(requester=request.user, recipient=requested_skill.user, offered_skill=offered_skill, requested_skill=requested_skill, status='pending').exists():
            messages.error(request, 'This swap request is already pending.')
        else:
            swap_request = SwapRequest.objects.create(requester=request.user, recipient=requested_skill.user, offered_skill=offered_skill, requested_skill=requested_skill, message=request.POST.get('message', ''))
            create_notification(requested_skill.user, 'New swap request', f'{request.user.username} wants to swap skills with you.', f'/swaps/{swap_request.id}/')
            create_activity(request.user, 'Sent a swap request', f'Requested {requested_skill.name} in exchange for {offered_skill.name}.')
            messages.success(request, 'Your swap request has been sent!')
            return redirect('request_detail', pk=swap_request.pk)
    return render(request, 'swap/send_request.html', {'requested_skill': requested_skill, 'offered_skills': offered_skills})

@login_required
@require_POST
def swap_action(request, pk):
    swap_request = get_object_or_404(SwapRequest, pk=pk)
    action = request.POST.get('action')
    if action in ['accept', 'decline'] and swap_request.recipient == request.user and swap_request.status == 'pending':
        swap_request.status = 'accepted' if action == 'accept' else 'declined'
        swap_request.save()
        create_notification(swap_request.requester, f'Swap request {swap_request.status}', f'{request.user.username} {swap_request.status} your swap request.', f'/swaps/{swap_request.id}/')
        create_activity(request.user, f'{swap_request.status.title()} a swap request', f'Swap with {swap_request.requester.username} was {swap_request.status}.')
        messages.success(request, f'Swap request {swap_request.status}.')
    elif action == 'cancel' and swap_request.requester == request.user and swap_request.status == 'pending':
        swap_request.status = 'cancelled'
        swap_request.save()
        create_notification(swap_request.recipient, 'Swap request cancelled', f'{request.user.username} cancelled their swap request.', f'/swaps/{swap_request.id}/')
        messages.success(request, 'Swap request cancelled.')
    elif action == 'complete' and request.user in [swap_request.requester, swap_request.recipient] and swap_request.status == 'accepted':
        swap_request.status = 'completed'
        swap_request.save()
        other_user = swap_request.other_user(request.user)
        create_notification(other_user, 'Swap completed', f'{request.user.username} marked your swap as completed. Leave a review when you are ready.', f'/swaps/{swap_request.id}/')
        create_activity(request.user, 'Completed a swap', f'Completed a swap with {other_user.username}.', 'bi bi-check-circle')
        messages.success(request, 'Swap marked as completed. You can now leave a review.')
    else:
        messages.error(request, 'That action is not available for this swap request.')
    return redirect('request_detail', pk=pk)

@login_required
def active_swaps(request):
    swaps = SwapRequest.objects.filter(Q(requester=request.user) | Q(recipient=request.user), status='accepted').select_related('requester', 'recipient', 'offered_skill', 'requested_skill').order_by('-updated_at')
    return render(request, 'swap/active_swaps.html', {'swaps': swaps})

@login_required
def completed_swaps(request):
    swaps = SwapRequest.objects.filter(Q(requester=request.user) | Q(recipient=request.user), status='completed').select_related('requester', 'recipient', 'offered_skill', 'requested_skill').order_by('-updated_at')
    return render(request, 'swap/completed_swaps.html', {'swaps': swaps})

@login_required
@require_POST
def submit_review(request, pk):
    swap_request = get_object_or_404(SwapRequest, pk=pk, status='completed')
    if request.user not in [swap_request.requester, swap_request.recipient]:
        return HttpResponseForbidden('You do not have permission to review this swap.')
    reviewed_user = swap_request.other_user(request.user)
    if Review.objects.filter(swap=swap_request, reviewer=request.user).exists():
        messages.error(request, 'You have already reviewed this swap.')
    else:
        try:
            rating = int(request.POST.get('rating'))
            if rating not in range(1, 6): raise ValueError
        except (TypeError, ValueError):
            messages.error(request, 'Please select a rating from 1 to 5.')
            return redirect('request_detail', pk=pk)
        Review.objects.create(reviewer=request.user, user=reviewed_user, swap=swap_request, rating=rating, comment=request.POST.get('comment', ''))
        review_stats = Review.objects.filter(user=reviewed_user).aggregate(average=Avg('rating'))
        reviewed_user.profile.rating = review_stats['average'] or 0
        reviewed_user.profile.reviews_count = Review.objects.filter(user=reviewed_user).count()
        reviewed_user.profile.save()
        create_notification(reviewed_user, 'You received a review', f'{request.user.username} left you a {rating}-star review.', f'/profile/{request.user.username}/')
        messages.success(request, 'Thanks for sharing your review!')
    return redirect('request_detail', pk=pk)

@login_required
def notifications(request):
    items = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'swap/notifications.html', {'notifications': items})

@login_required
@require_POST
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('notifications')

@login_required
def inbox(request):
    users = User.objects.filter(Q(received_messages__sender=request.user) | Q(sent_messages__recipient=request.user)).exclude(pk=request.user.pk).distinct()
    return render(request, 'swap/inbox.html', {'users': users})

@login_required
def conversation(request, username):
    other_user = get_object_or_404(User, username=username)
    if other_user == request.user:
        return redirect('inbox')
    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Message.objects.create(sender=request.user, recipient=other_user, body=body)
            create_notification(other_user, 'New message', f'{request.user.username} sent you a message.', f'/messages/{request.user.username}/')
        return redirect('conversation', username=other_user.username)
    thread = Message.objects.filter(Q(sender=request.user, recipient=other_user) | Q(sender=other_user, recipient=request.user))
    thread.filter(recipient=request.user, is_read=False).update(is_read=True)
    return render(request, 'swap/conversation.html', {'other_user': other_user, 'thread': thread})
