from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification


@login_required
def notification_list(request):
    """Display all notifications for the user"""
    notifications = request.user.notifications.all()
    unread_count = notifications.filter(is_read=False).count()
    
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })


@login_required
@require_POST
def mark_as_read(request, notification_id):
    """Mark a single notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('notifications:notification_list')


@login_required
@require_POST
def mark_all_as_read(request):
    """Mark all notifications as read"""
    request.user.notifications.filter(is_read=False).update(is_read=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('notifications:notification_list')


@login_required
def get_unread_count(request):
    """Get the count of unread notifications (for AJAX calls)"""
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def get_recent_notifications(request):
    """Get recent notifications for dropdown (AJAX)"""
    notifications = request.user.notifications.all()[:5]
    unread_count = request.user.notifications.filter(is_read=False).count()
    
    data = {
        'notifications': [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message[:100] + '...' if len(n.message) > 100 else n.message,
                'link': n.link or '',
                'is_read': n.is_read,
                'created_at': n.created_at.strftime('%b %d, %I:%M %p'),
                'type': n.notification_type
            }
            for n in notifications
        ],
        'unread_count': unread_count
    }
    return JsonResponse(data)
