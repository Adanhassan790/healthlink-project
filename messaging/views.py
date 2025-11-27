from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Conversation, Message
from appointments.models import Appointment
import json

@login_required
def conversation_list(request):
    """List all conversations for the current user"""
    if request.user.user_type == 'patient':
        conversations = Conversation.objects.filter(patient=request.user)
    elif request.user.user_type == 'doctor':
        conversations = Conversation.objects.filter(doctor=request.user)
    else:
        conversations = Conversation.objects.none()
    
    conversations = conversations.order_by('-updated_at')
    
    return render(request, 'messaging/conversations.html', {
        'conversations': conversations
    })

@login_required
def conversation_detail(request, conversation_id):
    """View a specific conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check if user is part of this conversation
    if request.user not in [conversation.patient, conversation.doctor]:
        return redirect('conversation_list')
    
    # Mark messages as read
    if request.user != conversation.doctor:
        conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    messages = conversation.messages.all()
    
    return render(request, 'messaging/conversation.html', {
        'conversation': conversation,
        'messages': messages
    })

@login_required
def send_message(request, conversation_id):
    """Send a new message in a conversation"""
    if request.method == 'POST':
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        # Check if user is part of this conversation
        if request.user not in [conversation.patient, conversation.doctor]:
            return JsonResponse({'error': 'Not authorized'}, status=403)
        
        content = request.POST.get('content', '').strip()
        if content:
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            
            # Update conversation timestamp
            conversation.save()
            
            return JsonResponse({
                'success': True,
                'message_id': message.id,
                'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def start_conversation(request, appointment_id):
    """Start a new conversation for an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if user is part of this appointment
    if request.user not in [appointment.patient, appointment.doctor]:
        return redirect('conversation_list')
    
    # Get or create conversation
    conversation, created = Conversation.objects.get_or_create(
        patient=appointment.patient,
        doctor=appointment.doctor,
        appointment=appointment
    )
    
    return redirect('messaging:conversation_detail', conversation_id=conversation.id)

@login_required
def get_unread_count(request):
    """Get number of unread messages for the current user"""
    if request.user.user_type == 'patient':
        unread_count = Message.objects.filter(
            conversation__patient=request.user,
            is_read=False
        ).exclude(sender=request.user).count()
    elif request.user.user_type == 'doctor':
        unread_count = Message.objects.filter(
            conversation__doctor=request.user,
            is_read=False
        ).exclude(sender=request.user).count()
    else:
        unread_count = 0
    
    return JsonResponse({'unread_count': unread_count})