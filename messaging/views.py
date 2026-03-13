from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Conversation, Message, VideoCall
from appointments.models import Appointment
from notifications.models import notify_new_message
import json
import uuid

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
        return redirect('messaging:conversation_list')
    
    # Check if user wants to start a video call directly
    if request.GET.get('start_video') == '1':
        receiver = conversation.doctor if request.user == conversation.patient else conversation.patient
        
        # Check for existing active call (use correct status values)
        existing_call = VideoCall.objects.filter(
            conversation=conversation,
            status__in=['initiated', 'ringing', 'ongoing']
        ).first()
        
        if existing_call:
            return redirect('messaging:video_room', room_id=existing_call.room_id)
        
        # Create new video call
        room_id = f"healthlink-{conversation.id}-{uuid.uuid4().hex[:8]}"
        video_call = VideoCall.objects.create(
            room_id=room_id,
            conversation=conversation,
            caller=request.user,
            receiver=receiver,
            status='initiated'
        )
        return redirect('messaging:video_room', room_id=room_id)
    
    # Mark messages as read
    if request.user != conversation.doctor:
        conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    messages = conversation.messages.all()
    
    # GET PATIENT PROFILE INFORMATION FOR DOCTORS
    patient_profile = None
    appointment_symptoms = None
    
    if request.user.user_type == 'doctor':
        # Try to get patient profile if you have one
        try:
            from users.models import PatientProfile
            patient_profile = PatientProfile.objects.get(user=conversation.patient)
        except:
            patient_profile = None
        
        # Get appointment symptoms
        if conversation.appointment:
            appointment_symptoms = conversation.appointment.symptoms
    
    return render(request, 'messaging/conversation.html', {
        'conversation': conversation,
        'messages': messages,
        'patient_profile': patient_profile,  # Pass to template
        'appointment_symptoms': appointment_symptoms,  # Pass to template
        'current_user_type': request.user.user_type  # Help identify user role
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
            
            # Notify the receiver about the new message
            receiver = conversation.doctor if request.user == conversation.patient else conversation.patient
            notify_new_message(request.user, receiver, conversation)
            
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
        return redirect('messaging:conversation_list')
    
    # Get or create conversation
    conversation, created = Conversation.objects.get_or_create(
        patient=appointment.patient,
        doctor=appointment.doctor,
        appointment=appointment
    )
    
    # Check if user wants to start a video call directly
    if request.GET.get('video') == '1':
        # Create video call and redirect to video room
        receiver = appointment.doctor if request.user == appointment.patient else appointment.patient
        
        # Check for existing active call (use correct status values)
        existing_call = VideoCall.objects.filter(
            conversation=conversation,
            status__in=['initiated', 'ringing', 'ongoing']
        ).first()
        
        if existing_call:
            return redirect('messaging:video_room', room_id=existing_call.room_id)
        
        # Create new video call
        room_id = f"healthlink-{conversation.id}-{uuid.uuid4().hex[:8]}"
        video_call = VideoCall.objects.create(
            room_id=room_id,
            conversation=conversation,
            caller=request.user,
            receiver=receiver,
            status='initiated'
        )
        return redirect('messaging:video_room', room_id=room_id)
    
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


# ============== VIDEO CALL VIEWS ==============

@login_required
def start_video_call(request, conversation_id):
    """Start a video call in a conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    print(f"\n=== START_VIDEO_CALL ===")
    print(f"User: {request.user.username}, Conversation: {conversation_id}")
    
    # Check if user is part of this conversation
    if request.user not in [conversation.patient, conversation.doctor]:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    # Determine caller and receiver
    if request.user == conversation.patient:
        receiver = conversation.doctor
    else:
        receiver = conversation.patient
    
    # Check for existing active call (use correct status values)
    existing_call = VideoCall.objects.filter(
        conversation=conversation,
        status__in=['initiated', 'ringing', 'ongoing']
    ).first()
    
    print(f"Existing call found: {existing_call}")
    
    if existing_call:
        print(f"Joining existing call: {existing_call.id}, room: {existing_call.room_id}")
        return JsonResponse({
            'success': True,
            'call_id': existing_call.id,
            'room_id': existing_call.room_id,
            'status': existing_call.status,
            'message': 'Joining existing call'
        })
    
    # Create new video call
    room_id = f"healthlink-{conversation.id}-{uuid.uuid4().hex[:8]}"
    print(f"Creating NEW call with room: {room_id}")
    
    video_call = VideoCall.objects.create(
        room_id=room_id,
        conversation=conversation,
        caller=request.user,
        receiver=receiver,
        status='initiated'
    )
    
    print(f"Created call ID: {video_call.id}")
    
    return JsonResponse({
        'success': True,
        'call_id': video_call.id,
        'room_id': room_id,
        'status': 'initiated'
    })

@login_required
def join_video_call(request, call_id):
    """Join an existing video call"""
    video_call = get_object_or_404(VideoCall, id=call_id)
    conversation = video_call.conversation
    
    # Check if user is part of this conversation
    if request.user not in [conversation.patient, conversation.doctor]:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    if video_call.status in ['initiated', 'ringing']:
        video_call.status = 'ongoing'
        video_call.answered_at = timezone.now()
        video_call.save()
    
    return JsonResponse({
        'success': True,
        'call_id': video_call.id,
        'room_id': video_call.room_id,
        'status': video_call.status,
        'caller_name': video_call.caller.get_full_name() or video_call.caller.username,
        'receiver_name': video_call.receiver.get_full_name() or video_call.receiver.username,
        'is_caller': request.user == video_call.caller
    })

@login_required
def end_video_call(request, call_id):
    """End a video call"""
    video_call = get_object_or_404(VideoCall, id=call_id)
    conversation = video_call.conversation
    
    # Check if user is part of this conversation
    if request.user not in [conversation.patient, conversation.doctor]:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    video_call.status = 'ended'
    video_call.ended_at = timezone.now()
    
    # Calculate duration if call was answered
    if video_call.answered_at:
        duration = (video_call.ended_at - video_call.answered_at).total_seconds()
        video_call.duration = int(duration)
    
    video_call.save()
    
    return JsonResponse({
        'success': True,
        'status': 'ended',
        'duration': video_call.duration
    })

@login_required
def decline_video_call(request, call_id):
    """Decline an incoming video call"""
    video_call = get_object_or_404(VideoCall, id=call_id)
    conversation = video_call.conversation
    
    # Check if user is part of this conversation
    if request.user not in [conversation.patient, conversation.doctor]:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    video_call.status = 'declined'
    video_call.ended_at = timezone.now()
    video_call.save()
    
    return JsonResponse({
        'success': True,
        'status': 'declined'
    })

@login_required
def get_call_status(request, call_id):
    """Get the current status of a video call"""
    video_call = get_object_or_404(VideoCall, id=call_id)
    conversation = video_call.conversation
    
    # Check if user is part of this conversation
    if request.user not in [conversation.patient, conversation.doctor]:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    return JsonResponse({
        'call_id': video_call.id,
        'room_id': video_call.room_id,
        'status': video_call.status,
        'caller_name': video_call.caller.get_full_name() or video_call.caller.username,
        'is_caller': request.user == video_call.caller,
        'duration': video_call.duration
    })

@login_required
def check_incoming_call(request, conversation_id):
    """Check if there's an incoming call for this conversation"""
    print(f"\n=== CHECK_INCOMING_CALL ===")
    print(f"User: {request.user.username}, Conversation ID: {conversation_id}")
    
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check if user is part of this conversation
    if request.user not in [conversation.patient, conversation.doctor]:
        print(f"User not authorized!")
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    # Look for pending calls where user is the receiver
    incoming_call = VideoCall.objects.filter(
        conversation=conversation,
        receiver=request.user,
        status__in=['initiated', 'ringing']
    ).first()
    
    print(f"Incoming call found: {incoming_call}")
    
    if incoming_call:
        print(f"Returning call info: ID={incoming_call.id}, caller={incoming_call.caller.username}")
        return JsonResponse({
            'has_incoming_call': True,
            'call_id': incoming_call.id,
            'room_id': incoming_call.room_id,
            'caller_name': incoming_call.caller.get_full_name() or incoming_call.caller.username
        })
    
    return JsonResponse({'has_incoming_call': False})

@login_required
def video_room(request, room_id):
    """Render the video call room"""
    print(f"\n=== VIDEO_ROOM ===")
    print(f"User: {request.user.username}, Room ID: {room_id}")
    
    video_call = get_object_or_404(VideoCall, room_id=room_id)
    print(f"VideoCall ID: {video_call.id}, Status: {video_call.status}")
    print(f"Caller: {video_call.caller.username}, Receiver: {video_call.receiver.username}")
    
    conversation = video_call.conversation
    
    # Check if user is part of this conversation
    if request.user not in [conversation.patient, conversation.doctor]:
        return redirect('messaging:conversation_list')
    
    # Get the other participant
    if request.user == conversation.patient:
        other_user = conversation.doctor
    else:
        other_user = conversation.patient
    
    is_caller = request.user == video_call.caller
    print(f"Is caller: {is_caller}")
    
    return render(request, 'messaging/video_room.html', {
        'video_call': video_call,
        'conversation': conversation,
        'other_user': other_user,
        'is_caller': is_caller
    })


@login_required
def register_peer(request, call_id):
    """Register a peer ID for a video call participant"""
    print(f"\n=== REGISTER_PEER ===")
    print(f"User: {request.user.username}, Call ID: {call_id}")
    
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    video_call = get_object_or_404(VideoCall, id=call_id)
    conversation = video_call.conversation
    
    # Check if user is part of this conversation
    if request.user not in [conversation.patient, conversation.doctor]:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        peer_id = data.get('peer_id')
        role = data.get('role')
        
        print(f"Peer ID: {peer_id[:30]}..., Role: {role}")
        
        if not peer_id:
            return JsonResponse({'error': 'peer_id required'}, status=400)
        
        # Store the peer ID based on role
        if role == 'caller' or request.user == video_call.caller:
            video_call.caller_peer_id = peer_id
            print(f"Saved as CALLER peer")
        else:
            video_call.receiver_peer_id = peer_id
            print(f"Saved as RECEIVER peer")
        
        video_call.save()
        print(f"Call now has: caller_peer={video_call.caller_peer_id[:20] if video_call.caller_peer_id else None}..., receiver_peer={video_call.receiver_peer_id[:20] if video_call.receiver_peer_id else None}...")
        
        return JsonResponse({
            'success': True,
            'message': 'Peer registered'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@login_required  
def get_peer(request, call_id):
    """Get the other participant's peer ID"""
    video_call = get_object_or_404(VideoCall, id=call_id)
    conversation = video_call.conversation
    
    # Check if user is part of this conversation
    if request.user not in [conversation.patient, conversation.doctor]:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    # Determine which peer ID to return based on requested role
    requested_role = request.GET.get('role', '')
    
    if requested_role == 'caller':
        peer_id = video_call.caller_peer_id
    elif requested_role == 'receiver':
        peer_id = video_call.receiver_peer_id
    else:
        # Return the other person's peer ID
        if request.user == video_call.caller:
            peer_id = video_call.receiver_peer_id
        else:
            peer_id = video_call.caller_peer_id
    
    return JsonResponse({
        'peer_id': peer_id,
        'caller_peer_id': video_call.caller_peer_id,
        'receiver_peer_id': video_call.receiver_peer_id
    })


# ============== WEBRTC SIGNALING VIEWS ==============

@login_required
def send_offer(request, call_id):
    """Caller sends WebRTC offer (SDP)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    video_call = get_object_or_404(VideoCall, id=call_id)
    conversation = video_call.conversation
    
    if request.user not in [conversation.patient, conversation.doctor]:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        offer = data.get('offer')
        
        if not offer:
            return JsonResponse({'error': 'offer required'}, status=400)
        
        video_call.caller_offer = json.dumps(offer)
        video_call.status = 'ringing'
        video_call.save()
        
        return JsonResponse({'success': True})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@login_required
def get_offer(request, call_id):
    """Receiver gets the WebRTC offer"""
    video_call = get_object_or_404(VideoCall, id=call_id)
    conversation = video_call.conversation
    
    if request.user not in [conversation.patient, conversation.doctor]:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    if video_call.caller_offer:
        return JsonResponse({
            'offer': json.loads(video_call.caller_offer),
            'status': video_call.status
        })
    
    return JsonResponse({'offer': None, 'status': video_call.status})


@login_required
def send_answer(request, call_id):
    """Receiver sends WebRTC answer (SDP)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    video_call = get_object_or_404(VideoCall, id=call_id)
    conversation = video_call.conversation
    
    if request.user not in [conversation.patient, conversation.doctor]:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        answer = data.get('answer')
        
        if not answer:
            return JsonResponse({'error': 'answer required'}, status=400)
        
        video_call.receiver_answer = json.dumps(answer)
        video_call.status = 'ongoing'
        video_call.answered_at = timezone.now()
        video_call.save()
        
        return JsonResponse({'success': True})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@login_required
def get_answer(request, call_id):
    """Caller gets the WebRTC answer"""
    video_call = get_object_or_404(VideoCall, id=call_id)
    conversation = video_call.conversation
    
    if request.user not in [conversation.patient, conversation.doctor]:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    if video_call.receiver_answer:
        return JsonResponse({
            'answer': json.loads(video_call.receiver_answer),
            'status': video_call.status
        })
    
    return JsonResponse({'answer': None, 'status': video_call.status})


@login_required
def send_ice_candidate(request, call_id):
    """Send an ICE candidate"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    video_call = get_object_or_404(VideoCall, id=call_id)
    conversation = video_call.conversation
    
    if request.user not in [conversation.patient, conversation.doctor]:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        candidate = data.get('candidate')
        
        if not candidate:
            return JsonResponse({'error': 'candidate required'}, status=400)
        
        is_caller = request.user == video_call.caller
        
        # Get existing candidates or start fresh
        if is_caller:
            existing = video_call.caller_ice_candidates
            candidates = json.loads(existing) if existing else []
            candidates.append(candidate)
            video_call.caller_ice_candidates = json.dumps(candidates)
        else:
            existing = video_call.receiver_ice_candidates
            candidates = json.loads(existing) if existing else []
            candidates.append(candidate)
            video_call.receiver_ice_candidates = json.dumps(candidates)
        
        video_call.save()
        
        return JsonResponse({'success': True})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@login_required
def get_ice_candidates(request, call_id):
    """Get ICE candidates from the other participant"""
    video_call = get_object_or_404(VideoCall, id=call_id)
    conversation = video_call.conversation
    
    if request.user not in [conversation.patient, conversation.doctor]:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    is_caller = request.user == video_call.caller
    
    # Get the OTHER person's candidates
    if is_caller:
        candidates_json = video_call.receiver_ice_candidates
    else:
        candidates_json = video_call.caller_ice_candidates
    
    candidates = json.loads(candidates_json) if candidates_json else []
    
    # Also return last received index to allow incremental fetching
    last_index = request.GET.get('last_index', -1)
    try:
        last_index = int(last_index)
    except:
        last_index = -1
    
    new_candidates = candidates[last_index + 1:] if last_index >= 0 else candidates
    
    return JsonResponse({
        'candidates': new_candidates,
        'total': len(candidates),
        'status': video_call.status
    })


@login_required
def get_signaling_state(request, call_id):
    """Get the full signaling state for debugging/syncing"""
    video_call = get_object_or_404(VideoCall, id=call_id)
    conversation = video_call.conversation
    
    if request.user not in [conversation.patient, conversation.doctor]:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    is_caller = request.user == video_call.caller
    
    return JsonResponse({
        'call_id': video_call.id,
        'status': video_call.status,
        'is_caller': is_caller,
        'has_offer': bool(video_call.caller_offer),
        'has_answer': bool(video_call.receiver_answer),
        'caller_ice_count': len(json.loads(video_call.caller_ice_candidates)) if video_call.caller_ice_candidates else 0,
        'receiver_ice_count': len(json.loads(video_call.receiver_ice_candidates)) if video_call.receiver_ice_candidates else 0,
    })