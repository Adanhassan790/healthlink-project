from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count
from .models import Conversation, Message, VideoCall
from appointments.models import Appointment
from notifications.models import notify_new_message
from .vonage_service import create_session, generate_token, get_api_key
import json
import uuid
import logging

logger = logging.getLogger(__name__)


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
        
        # Create new video call with Vonage session
        try:
            room_id = f"healthlink-{conversation.id}-{uuid.uuid4().hex[:8]}"
            vonage_session_id = create_session()
            
            video_call = VideoCall.objects.create(
                room_id=room_id,
                conversation=conversation,
                caller=request.user,
                receiver=receiver,
                status='initiated',
                vonage_session_id=vonage_session_id
            )
            logger.info(f"Created video call {video_call.id} with Vonage session {vonage_session_id}")
            return redirect('messaging:video_room', room_id=room_id)
        except Exception as e:
            logger.error(f"Error creating Vonage session: {str(e)}")
            # Fall back to creating call without session (will fail when joining)
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
    # Only allow POST requests
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
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
    logger.info(f"\n=== VIDEO_ROOM ===")
    logger.info(f"User: {request.user.username}, Room ID: {room_id}")
    
    video_call = get_object_or_404(VideoCall, room_id=room_id)
    logger.info(f"VideoCall ID: {video_call.id}, Status: {video_call.status}")
    logger.info(f"Caller: {video_call.caller.username}, Receiver: {video_call.receiver.username}")
    
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
    logger.info(f"Is caller: {is_caller}")
    
    # Generate Vonage token for this user
    vonage_error = None
    api_key = None
    token = None
    
    try:
        # Check if Vonage is configured
        api_key = get_api_key()
        logger.info(f"Vonage API Key found: {api_key[:10] if api_key else 'MISSING'}...")
        
        # Create session if needed
        if not video_call.vonage_session_id:
            logger.info("Creating new Vonage session...")
            video_call.vonage_session_id = create_session()
            video_call.save()
            logger.info(f"Session created: {video_call.vonage_session_id}")
        
        # Generate token for this user
        logger.info("Generating Vonage token...")
        user_id = f"{request.user.id}_{request.user.username}"
        token = generate_token(video_call.vonage_session_id, user_id=user_id)
        logger.info(f"Token generated successfully")
        
    except ImportError as e:
        error_msg = f"OpenTok library not installed: {str(e)}. Please install opentok package."
        logger.error(error_msg)
        vonage_error = error_msg
    except ValueError as e:
        error_msg = f"Vonage not configured: {str(e)}"
        logger.error(error_msg)
        vonage_error = error_msg
    except Exception as e:
        error_msg = f"Error with Vonage: {str(e)}"
        logger.error(error_msg)
        vonage_error = error_msg
    
    context = {
        'video_call': video_call,
        'conversation': conversation,
        'other_user': other_user,
        'is_caller': is_caller,
        'vonage_api_key': api_key or '',
        'vonage_session_id': video_call.vonage_session_id or '',
        'vonage_token': token or '',
        'vonage_error': vonage_error or '',
        'user_display_name': request.user.get_full_name() or request.user.username
    }
    
    return render(request, 'messaging/video_room.html', context)


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


# ============== CALL HISTORY & STATISTICS ==============

@login_required
def call_history(request, conversation_id):
    """Get call history for a conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check if user is part of this conversation
    if request.user not in [conversation.patient, conversation.doctor]:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    # Get all calls for this conversation
    calls = VideoCall.objects.filter(conversation=conversation).order_by('-started_at')
    
    call_data = []
    for call in calls:
        call_data.append({
            'id': call.id,
            'caller': call.caller.get_full_name() or call.caller.username,
            'receiver': call.receiver.get_full_name() or call.receiver.username,
            'status': call.status,
            'duration': call.duration_formatted,
            'duration_seconds': call.duration,
            'started_at': call.started_at.isoformat(),
            'answered_at': call.answered_at.isoformat() if call.answered_at else None,
            'ended_at': call.ended_at.isoformat() if call.ended_at else None,
        })
    
    return JsonResponse({
        'conversation_id': conversation_id,
        'total_calls': len(call_data),
        'calls': call_data
    })


@login_required
def call_statistics(request, conversation_id=None):
    """Get call statistics for a conversation or user"""
    if conversation_id:
        # Statistics for specific conversation
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        if request.user not in [conversation.patient, conversation.doctor]:
            return JsonResponse({'error': 'Not authorized'}, status=403)
        
        calls = VideoCall.objects.filter(conversation=conversation)
    else:
        # Statistics for current user (all calls they participated in)
        calls = VideoCall.objects.filter(
            Q(caller=request.user) | Q(receiver=request.user)
        )
    
    # Calculate statistics
    total_calls = calls.count()
    completed_calls = calls.filter(status__in=['ended', 'ongoing']).count()
    missed_calls = calls.filter(status='missed').count()
    declined_calls = calls.filter(status='declined').count()
    
    # Calculate total duration
    total_duration = 0
    for call in calls.filter(status__in=['ended', 'ongoing']):
        total_duration += call.duration
    
    average_duration = total_duration // completed_calls if completed_calls > 0 else 0
    
    # Get calls by month (last 6 months)
    from django.db.models import Count
    from datetime import timedelta
    from django.utils import timezone
    
    six_months_ago = timezone.now() - timedelta(days=180)
    calls_by_month = calls.filter(started_at__gte=six_months_ago).values(
        'started_at__year', 'started_at__month'
    ).annotate(count=Count('id')).order_by('started_at__year', 'started_at__month')
    
    month_data = [{'year': item['started_at__year'], 'month': item['started_at__month'], 'count': item['count']} for item in calls_by_month]
    
    stats = {
        'total_calls': total_calls,
        'completed_calls': completed_calls,
        'missed_calls': missed_calls,
        'declined_calls': declined_calls,
        'total_duration_seconds': total_duration,
        'average_duration_seconds': average_duration,
        'completion_rate': round((completed_calls / total_calls * 100) if total_calls > 0 else 0, 1),
        'calls_by_month': month_data
    }
    
    return JsonResponse(stats)


@login_required
def call_statistics_dashboard(request):
    """Render call statistics dashboard"""
    # Get user's conversations
    if request.user.user_type == 'patient':
        conversations = Conversation.objects.filter(patient=request.user)
    elif request.user.user_type == 'doctor':
        conversations = Conversation.objects.filter(doctor=request.user)
    else:
        conversations = Conversation.objects.none()
    
    # Calculate overall stats
    from django.db.models import Count, Q
    all_calls = VideoCall.objects.filter(
        Q(caller=request.user) | Q(receiver=request.user)
    )
    
    stats = {
        'total_calls': all_calls.count(),
        'completed_calls': all_calls.filter(status__in=['ended', 'ongoing']).count(),
        'missed_calls': all_calls.filter(status='missed').count(),
        'declined_calls': all_calls.filter(status='declined').count(),
    }
    
    # Get total duration in minutes
    total_seconds = sum([call.duration for call in all_calls.filter(status__in=['ended', 'ongoing'])])
    stats['total_minutes'] = total_seconds // 60
    
    return render(request, 'messaging/call_statistics.html', {
        'conversations': conversations,
        'stats': stats
    })


@login_required
def toggle_call_recording(request, call_id):
    """Enable or disable recording for a call"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    video_call = get_object_or_404(VideoCall, id=call_id)
    conversation = video_call.conversation
    
    # Check if user is part of this conversation (only caller/receiver can toggle)
    if request.user not in [conversation.patient, conversation.doctor]:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    # Only allow toggling if call hasn't ended yet or just ended
    if video_call.status not in ['initiated', 'ringing', 'ongoing', 'ended']:
        return JsonResponse({'error': 'Cannot modify recording for this call status'}, status=400)
    
    try:
        data = json.loads(request.body)
        enabled = data.get('enabled', False)
        
        video_call.recording_enabled = enabled
        video_call.save()
        
        return JsonResponse({
            'success': True,
            'recording_enabled': video_call.recording_enabled,
            'message': f'Recording {"enabled" if enabled else "disabled"}'
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


# ============== DIAGNOSTICS ==============

@login_required
def video_call_diagnostics(request, conversation_id):
    """Diagnostics endpoint to check video call configuration"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check if user is part of this conversation
    if request.user not in [conversation.patient, conversation.doctor]:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    # Get all calls for this conversation
    calls = VideoCall.objects.filter(conversation=conversation).order_by('-started_at')[:5]
    
    diag_data = {
        'conversation_id': conversation_id,
        'user': {
            'username': request.user.username,
            'full_name': request.user.get_full_name(),
            'email': request.user.email,
            'user_type': request.user.user_type
        },
        'conversation': {
            'patient': conversation.patient.get_full_name() or conversation.patient.username,
            'doctor': conversation.doctor.get_full_name() or conversation.doctor.username,
            'created_at': conversation.created_at.isoformat(),
            'updated_at': conversation.updated_at.isoformat()
        },
        'recent_calls': []
    }
    
    for call in calls:
        diag_data['recent_calls'].append({
            'id': call.id,
            'room_id': call.room_id,
            'status': call.status,
            'caller': call.caller.username,
            'receiver': call.receiver.username,
            'started_at': call.started_at.isoformat(),
            'answered_at': call.answered_at.isoformat() if call.answered_at else None,
            'duration': call.duration,
            'has_offer': bool(call.caller_offer),
            'has_answer': bool(call.receiver_answer)
        })
    
    return JsonResponse(diag_data)