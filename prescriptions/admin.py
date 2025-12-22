from django.contrib import admin
from .models import Medication, Prescription, PrescriptionItem, PrescriptionHistory


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'generic_name', 'form', 'strength', 'category', 'requires_prescription', 'is_active']
    list_filter = ['category', 'form', 'requires_prescription', 'is_controlled', 'is_active']
    search_fields = ['name', 'generic_name', 'manufacturer']
    ordering = ['name']


class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1
    autocomplete_fields = ['medication']


class PrescriptionHistoryInline(admin.TabularInline):
    model = PrescriptionHistory
    extra = 0
    readonly_fields = ['action', 'performed_by', 'notes', 'timestamp']
    can_delete = False


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['prescription_number', 'patient', 'doctor', 'status', 'created_at', 'valid_until', 'is_signed']
    list_filter = ['status', 'is_signed', 'created_at']
    search_fields = ['prescription_number', 'patient__username', 'doctor__username', 'diagnosis']
    readonly_fields = ['prescription_number', 'created_at', 'updated_at', 'signed_at', 'dispensed_at']
    date_hierarchy = 'created_at'
    inlines = [PrescriptionItemInline, PrescriptionHistoryInline]
    
    fieldsets = (
        ('Prescription Info', {
            'fields': ('prescription_number', 'status', 'is_signed')
        }),
        ('Parties', {
            'fields': ('doctor', 'patient', 'appointment')
        }),
        ('Medical Details', {
            'fields': ('diagnosis', 'notes')
        }),
        ('Dates', {
            'fields': ('valid_until', 'created_at', 'updated_at', 'signed_at', 'dispensed_at')
        }),
    )


@admin.register(PrescriptionItem)
class PrescriptionItemAdmin(admin.ModelAdmin):
    list_display = ['prescription', 'medication', 'dosage', 'frequency', 'quantity']
    list_filter = ['frequency', 'duration_unit']
    search_fields = ['prescription__prescription_number', 'medication__name']
    autocomplete_fields = ['medication', 'prescription']


@admin.register(PrescriptionHistory)
class PrescriptionHistoryAdmin(admin.ModelAdmin):
    list_display = ['prescription', 'action', 'performed_by', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['prescription__prescription_number']
    readonly_fields = ['prescription', 'action', 'performed_by', 'notes', 'timestamp']
