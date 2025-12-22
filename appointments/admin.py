from django.contrib import admin
from .models import Specialty, Appointment, DoctorAvailability, DoctorReview

admin.site.register(Specialty)
admin.site.register(Appointment)

@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day_of_week', 'start_time', 'end_time', 'is_available']
    list_filter = ['doctor', 'day_of_week', 'is_available']
    ordering = ['doctor', 'day_of_week', 'start_time']


@admin.register(DoctorReview)
class DoctorReviewAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'patient', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['doctor__username', 'patient__username', 'comment']
    readonly_fields = ['created_at']