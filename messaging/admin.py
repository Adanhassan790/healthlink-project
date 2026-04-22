from django.contrib import admin
from django.utils.html import format_html
from .models import Conversation, Message, VideoCall


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_info', 'doctor_info', 'message_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('patient__username', 'doctor__username', 'patient__email', 'doctor__email')
    readonly_fields = ('created_at', 'updated_at', 'message_count_display')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Participants', {
            'fields': ('patient', 'doctor', 'appointment')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'message_count_display'),
            'classes': ('collapse',)
        })
    )
    
    def patient_info(self, obj):
        """Display patient name with link"""
        return format_html(
            '<a href="/admin/users/customuser/{}/change/">{}</a>',
            obj.patient.id,
            obj.patient.get_full_name() or obj.patient.username
        )
    patient_info.short_description = 'Patient'
    
    def doctor_info(self, obj):
        """Display doctor name with link"""
        return format_html(
            '<a href="/admin/users/customuser/{}/change/">{}</a>',
            obj.doctor.id,
            obj.doctor.get_full_name() or obj.doctor.username
        )
    doctor_info.short_description = 'Doctor'
    
    def message_count(self, obj):
        """Show count of messages"""
        count = obj.messages.count()
        return format_html(
            '<span style="background-color: #417690; color: white; padding: 3px 10px; border-radius: 12px;">{}</span>',
            count
        )
    message_count.short_description = 'Messages'
    
    def message_count_display(self, obj):
        """Display total message count"""
        return obj.messages.count()
    message_count_display.short_description = 'Total Messages'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender_info', 'conversation_info', 'content_preview', 'is_read', 'timestamp')
    list_filter = ('is_read', 'timestamp', 'sender__user_type')
    search_fields = ('sender__username', 'content', 'conversation__patient__username', 'conversation__doctor__username')
    readonly_fields = ('timestamp', 'content_display')
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Message Content', {
            'fields': ('conversation', 'sender', 'content', 'content_display')
        }),
        ('Status', {
            'fields': ('is_read', 'timestamp')
        })
    )
    
    def sender_info(self, obj):
        """Display sender with user type badge"""
        user_type_color = '#667eea' if obj.sender.user_type == 'doctor' else '#10b981'
        user_type_label = 'Dr.' if obj.sender.user_type == 'doctor' else 'Patient'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 8px; margin-right: 8px;">{}</span>{}',
            user_type_color,
            user_type_label,
            obj.sender.get_full_name() or obj.sender.username
        )
    sender_info.short_description = 'Sender'
    
    def conversation_info(self, obj):
        """Display conversation participants"""
        conv = obj.conversation
        return format_html(
            '#{}: {} ↔ {}',
            conv.id,
            conv.patient.username,
            conv.doctor.username
        )
    conversation_info.short_description = 'Conversation'
    
    def content_preview(self, obj):
        """Show message preview"""
        preview = obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        return preview
    content_preview.short_description = 'Content'
    
    def content_display(self, obj):
        """Display full content in readonly field"""
        return obj.content
    content_display.short_description = 'Full Content'


@admin.register(VideoCall)
class VideoCallAdmin(admin.ModelAdmin):
    list_display = ('id', 'call_participants', 'status_badge', 'duration_display', 'started_at', 'call_actions')
    list_filter = ('status', 'started_at', 'answered_at')
    search_fields = ('room_id', 'caller__username', 'receiver__username')
    readonly_fields = ('room_id', 'started_at', 'answered_at', 'ended_at', 'call_info', 'signaling_info')
    date_hierarchy = 'started_at'
    
    fieldsets = (
        ('Call Participants', {
            'fields': ('conversation', 'caller', 'receiver')
        }),
        ('Call Status', {
            'fields': ('status', 'status_badge_display', 'room_id')
        }),
        ('Call Timing', {
            'fields': ('started_at', 'answered_at', 'ended_at', 'duration')
        }),
        ('WebRTC Signaling', {
            'fields': ('signaling_info',),
            'classes': ('collapse',),
            'description': 'View detailed WebRTC signaling data'
        }),
        ('Additional Info', {
            'fields': ('call_info',),
            'classes': ('collapse',)
        })
    )
    
    def call_participants(self, obj):
        """Display caller and receiver"""
        return format_html(
            '<strong>{}</strong><br/>→ {}',
            obj.caller.get_full_name() or obj.caller.username,
            obj.receiver.get_full_name() or obj.receiver.username
        )
    call_participants.short_description = 'Participants'
    
    def status_badge(self, obj):
        """Show status with color coding"""
        status_colors = {
            'initiated': '#fbbf24',
            'ringing': '#f97316',
            'ongoing': '#10b981',
            'ended': '#6b7280',
            'missed': '#ef4444',
            'declined': '#dc2626'
        }
        color = status_colors.get(obj.status, '#95a3a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def status_badge_display(self, obj):
        """Same as status_badge for readonly field"""
        return self.status_badge(obj)
    status_badge_display.short_description = 'Current Status'
    
    def duration_display(self, obj):
        """Display call duration in readable format"""
        if obj.duration == 0:
            return '—'
        return format_html(
            '<span style="color: #667eea; font-weight: bold;">{}</span>',
            obj.duration_formatted
        )
    duration_display.short_description = 'Duration'
    
    def call_info(self, obj):
        """Display additional call information"""
        answered = '✓ Yes' if obj.answered_at else '✗ No'
        info_text = f"""
        <strong>Room ID:</strong> {obj.room_id}<br/>
        <strong>Call Answered:</strong> {answered}<br/>
        <strong>Duration:</strong> {obj.duration_formatted}<br/>
        <strong>Created:</strong> {obj.started_at.strftime('%Y-%m-%d %H:%M:%S')}<br/>
        """
        if obj.answered_at:
            info_text += f"<strong>Answered:</strong> {obj.answered_at.strftime('%Y-%m-%d %H:%M:%S')}<br/>"
        if obj.ended_at:
            info_text += f"<strong>Ended:</strong> {obj.ended_at.strftime('%Y-%m-%d %H:%M:%S')}<br/>"
        
        return format_html(info_text)
    call_info.short_description = 'Call Information'
    
    def signaling_info(self, obj):
        """Display WebRTC signaling information"""
        caller_ice_count = len(__import__('json').loads(obj.caller_ice_candidates)) if obj.caller_ice_candidates else 0
        receiver_ice_count = len(__import__('json').loads(obj.receiver_ice_candidates)) if obj.receiver_ice_candidates else 0
        
        info_text = f"""
        <strong>Caller Side:</strong><br/>
        • Peer ID: {obj.caller_peer_id or '—'}<br/>
        • Has Offer: {'✓' if obj.caller_offer else '✗'}<br/>
        • ICE Candidates: {caller_ice_count}<br/>
        <br/>
        <strong>Receiver Side:</strong><br/>
        • Peer ID: {obj.receiver_peer_id or '—'}<br/>
        • Has Answer: {'✓' if obj.receiver_answer else '✗'}<br/>
        • ICE Candidates: {receiver_ice_count}<br/>
        """
        return format_html(info_text)
    signaling_info.short_description = 'WebRTC Signaling Data'
    
    def call_actions(self, obj):
        """Quick action buttons"""
        if obj.status in ['initiated', 'ringing']:
            return format_html(
                '<span style="color: #f97316; font-weight: bold;">In Progress</span>'
            )
        elif obj.status == 'ongoing':
            return format_html(
                '<span style="color: #10b981; font-weight: bold;">Active</span>'
            )
        else:
            return '—'
    call_actions.short_description = 'Actions'
    
    def has_add_permission(self, request):
        """Disable adding new video calls from admin"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting video calls from admin"""
        return False
