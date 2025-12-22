from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import json

from .models import Prescription, PrescriptionItem, PrescriptionHistory, Medication
from .forms import PrescriptionForm, PrescriptionItemForm, QuickPrescriptionForm, MedicationSearchForm
from users.decorators import doctor_required, patient_required
from notifications.models import notify_prescription_created


def ensure_default_medications():
    """Create default medications if none exist"""
    if Medication.objects.count() < 20:
        medications = [
            # Painkillers
            ('Paracetamol', 'Acetaminophen', 'tablet', 'painkiller', '500mg'),
            ('Ibuprofen', 'Ibuprofen', 'tablet', 'antiinflammatory', '400mg'),
            ('Aspirin', 'Acetylsalicylic Acid', 'tablet', 'painkiller', '300mg'),
            ('Diclofenac', 'Diclofenac Sodium', 'tablet', 'antiinflammatory', '50mg'),
            ('Tramadol', 'Tramadol HCL', 'capsule', 'painkiller', '50mg'),
            
            # Antibiotics
            ('Amoxicillin', 'Amoxicillin', 'capsule', 'antibiotic', '500mg'),
            ('Azithromycin', 'Azithromycin', 'tablet', 'antibiotic', '250mg'),
            ('Ciprofloxacin', 'Ciprofloxacin', 'tablet', 'antibiotic', '500mg'),
            ('Metronidazole', 'Metronidazole', 'tablet', 'antibiotic', '400mg'),
            ('Doxycycline', 'Doxycycline', 'capsule', 'antibiotic', '100mg'),
            ('Cephalexin', 'Cefalexin', 'capsule', 'antibiotic', '500mg'),
            ('Clindamycin', 'Clindamycin', 'capsule', 'antibiotic', '300mg'),
            
            # Gastrointestinal
            ('Omeprazole', 'Omeprazole', 'capsule', 'gastrointestinal', '20mg'),
            ('Pantoprazole', 'Pantoprazole', 'tablet', 'gastrointestinal', '40mg'),
            ('Ranitidine', 'Ranitidine', 'tablet', 'gastrointestinal', '150mg'),
            ('Metoclopramide', 'Metoclopramide', 'tablet', 'gastrointestinal', '10mg'),
            ('Loperamide', 'Loperamide', 'capsule', 'gastrointestinal', '2mg'),
            ('Buscopan', 'Hyoscine Butylbromide', 'tablet', 'gastrointestinal', '10mg'),
            
            # Antihistamines
            ('Cetirizine', 'Cetirizine', 'tablet', 'antihistamine', '10mg'),
            ('Loratadine', 'Loratadine', 'tablet', 'antihistamine', '10mg'),
            ('Chlorpheniramine', 'Chlorpheniramine Maleate', 'tablet', 'antihistamine', '4mg'),
            ('Diphenhydramine', 'Diphenhydramine', 'tablet', 'antihistamine', '25mg'),
            
            # Respiratory
            ('Salbutamol', 'Salbutamol', 'inhaler', 'respiratory', '100mcg'),
            ('Fluticasone', 'Fluticasone Propionate', 'inhaler', 'respiratory', '250mcg'),
            ('Montelukast', 'Montelukast', 'tablet', 'respiratory', '10mg'),
            ('Ambroxol', 'Ambroxol', 'syrup', 'respiratory', '30mg/5ml'),
            ('Dextromethorphan', 'Dextromethorphan', 'syrup', 'respiratory', '15mg/5ml'),
            
            # Cardiovascular
            ('Amlodipine', 'Amlodipine', 'tablet', 'antihypertensive', '5mg'),
            ('Lisinopril', 'Lisinopril', 'tablet', 'antihypertensive', '10mg'),
            ('Atenolol', 'Atenolol', 'tablet', 'cardiovascular', '50mg'),
            ('Losartan', 'Losartan', 'tablet', 'antihypertensive', '50mg'),
            ('Hydrochlorothiazide', 'Hydrochlorothiazide', 'tablet', 'antihypertensive', '25mg'),
            ('Aspirin', 'Aspirin', 'tablet', 'cardiovascular', '75mg'),
            
            # Antidiabetic
            ('Metformin', 'Metformin', 'tablet', 'antidiabetic', '500mg'),
            ('Glibenclamide', 'Glibenclamide', 'tablet', 'antidiabetic', '5mg'),
            ('Glimepiride', 'Glimepiride', 'tablet', 'antidiabetic', '2mg'),
            
            # Mental Health
            ('Sertraline', 'Sertraline', 'tablet', 'antidepressant', '50mg'),
            ('Fluoxetine', 'Fluoxetine', 'capsule', 'antidepressant', '20mg'),
            ('Amitriptyline', 'Amitriptyline', 'tablet', 'antidepressant', '25mg'),
            ('Diazepam', 'Diazepam', 'tablet', 'sedative', '5mg'),
            ('Alprazolam', 'Alprazolam', 'tablet', 'sedative', '0.5mg'),
            
            # Vitamins/Supplements
            ('Vitamin C', 'Ascorbic Acid', 'tablet', 'vitamin', '500mg'),
            ('Vitamin D3', 'Cholecalciferol', 'tablet', 'vitamin', '1000IU'),
            ('Vitamin B Complex', 'B Complex', 'tablet', 'vitamin', ''),
            ('Iron', 'Ferrous Sulfate', 'tablet', 'vitamin', '200mg'),
            ('Calcium', 'Calcium Carbonate', 'tablet', 'vitamin', '500mg'),
            ('Folic Acid', 'Folic Acid', 'tablet', 'vitamin', '5mg'),
            
            # Topical
            ('Hydrocortisone Cream', 'Hydrocortisone', 'cream', 'antiinflammatory', '1%'),
            ('Clotrimazole Cream', 'Clotrimazole', 'cream', 'antifungal', '1%'),
            ('Mupirocin Ointment', 'Mupirocin', 'cream', 'antibiotic', '2%'),
            ('Betamethasone Cream', 'Betamethasone', 'cream', 'antiinflammatory', '0.1%'),
            
            # Eye/Ear Drops
            ('Ciprofloxacin Eye Drops', 'Ciprofloxacin', 'drops', 'antibiotic', '0.3%'),
            ('Chloramphenicol Eye Drops', 'Chloramphenicol', 'drops', 'antibiotic', '0.5%'),
            ('Artificial Tears', 'Carmellose Sodium', 'drops', 'other', '0.5%'),
        ]
        
        for med in medications:
            Medication.objects.get_or_create(
                name=med[0],
                defaults={
                    'generic_name': med[1],
                    'form': med[2],
                    'category': med[3],
                    'strength': med[4],
                }
            )
        print(f"✅ Created {len(medications)} default medications")


# ==================== DOCTOR VIEWS ====================

@login_required
@doctor_required
def prescription_list(request):
    """List all prescriptions for a doctor"""
    ensure_default_medications()
    
    prescriptions = Prescription.objects.filter(doctor=request.user).select_related('patient')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        prescriptions = prescriptions.filter(status=status)
    
    # Search
    search = request.GET.get('search')
    if search:
        prescriptions = prescriptions.filter(
            Q(prescription_number__icontains=search) |
            Q(patient__first_name__icontains=search) |
            Q(patient__last_name__icontains=search) |
            Q(diagnosis__icontains=search)
        )
    
    context = {
        'prescriptions': prescriptions,
        'status_filter': status,
        'search_query': search,
    }
    return render(request, 'prescriptions/prescription_list.html', context)


@login_required
@doctor_required
def create_prescription(request):
    """Create a new prescription"""
    ensure_default_medications()
    
    # Pre-populate from URL parameters (from appointment)
    initial_data = {}
    patient_id = request.GET.get('patient')
    appointment_id = request.GET.get('appointment')
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, doctor=request.user)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.doctor = request.user
            
            # Link to appointment if provided
            if appointment_id:
                from appointments.models import Appointment
                try:
                    appointment = Appointment.objects.get(pk=appointment_id)
                    prescription.appointment = appointment
                except Appointment.DoesNotExist:
                    pass
            
            prescription.save()
            
            # Create history entry
            PrescriptionHistory.objects.create(
                prescription=prescription,
                action='created',
                performed_by=request.user
            )
            
            messages.success(request, f'Prescription {prescription.prescription_number} created. Now add medications.')
            return redirect('prescriptions:add_items', pk=prescription.pk)
    else:
        # Pre-select patient if provided
        if patient_id:
            initial_data['patient'] = patient_id
        form = PrescriptionForm(doctor=request.user, initial=initial_data)
    
    context = {
        'form': form,
        'patient_id': patient_id,
        'appointment_id': appointment_id,
    }
    return render(request, 'prescriptions/create_prescription.html', context)


@login_required
@doctor_required
def add_prescription_items(request, pk):
    """Add medication items to a prescription"""
    prescription = get_object_or_404(Prescription, pk=pk, doctor=request.user)
    
    if prescription.status != 'draft':
        messages.error(request, 'Cannot modify a signed prescription.')
        return redirect('prescriptions:prescription_detail', pk=pk)
    
    if request.method == 'POST':
        form = PrescriptionItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.prescription = prescription
            item.save()
            messages.success(request, f'{item.medication.name} added to prescription.')
            return redirect('prescriptions:add_items', pk=pk)
    else:
        form = PrescriptionItemForm()
    
    context = {
        'prescription': prescription,
        'form': form,
        'items': prescription.items.all(),
        'medications': Medication.objects.filter(is_active=True),
    }
    return render(request, 'prescriptions/add_items.html', context)


@login_required
@doctor_required
def remove_prescription_item(request, pk, item_pk):
    """Remove an item from prescription"""
    prescription = get_object_or_404(Prescription, pk=pk, doctor=request.user)
    
    if prescription.status != 'draft':
        messages.error(request, 'Cannot modify a signed prescription.')
        return redirect('prescriptions:prescription_detail', pk=pk)
    
    item = get_object_or_404(PrescriptionItem, pk=item_pk, prescription=prescription)
    medication_name = item.medication.name
    item.delete()
    
    messages.success(request, f'{medication_name} removed from prescription.')
    return redirect('prescriptions:add_items', pk=pk)


@login_required
@doctor_required
def sign_prescription(request, pk):
    """Doctor signs the prescription"""
    prescription = get_object_or_404(Prescription, pk=pk, doctor=request.user)
    
    if prescription.status != 'draft':
        messages.error(request, 'Prescription is already signed or processed.')
        return redirect('prescriptions:prescription_detail', pk=pk)
    
    if not prescription.items.exists():
        messages.error(request, 'Cannot sign an empty prescription. Add at least one medication.')
        return redirect('prescriptions:add_items', pk=pk)
    
    prescription.sign_prescription()
    
    # Notify the patient about their new prescription
    notify_prescription_created(prescription.patient, request.user, prescription)
    
    PrescriptionHistory.objects.create(
        prescription=prescription,
        action='signed',
        performed_by=request.user,
        notes=f'Digitally signed by Dr. {request.user.get_full_name()}'
    )
    
    messages.success(request, f'Prescription {prescription.prescription_number} has been signed and is now active.')
    return redirect('prescriptions:prescription_detail', pk=pk)


@login_required
@doctor_required
def prescription_detail(request, pk):
    """View prescription details"""
    prescription = get_object_or_404(Prescription, pk=pk, doctor=request.user)
    
    context = {
        'prescription': prescription,
        'items': prescription.items.select_related('medication').all(),
        'history': prescription.history.all(),
    }
    return render(request, 'prescriptions/prescription_detail.html', context)


@login_required
@doctor_required
def cancel_prescription(request, pk):
    """Cancel a prescription"""
    prescription = get_object_or_404(Prescription, pk=pk, doctor=request.user)
    
    if prescription.status in ['dispensed', 'completed']:
        messages.error(request, 'Cannot cancel a dispensed prescription.')
        return redirect('prescriptions:prescription_detail', pk=pk)
    
    prescription.status = 'cancelled'
    prescription.save()
    
    PrescriptionHistory.objects.create(
        prescription=prescription,
        action='cancelled',
        performed_by=request.user
    )
    
    messages.success(request, f'Prescription {prescription.prescription_number} has been cancelled.')
    return redirect('prescriptions:prescription_list')


@login_required
@doctor_required
def quick_prescription(request):
    """Quick prescription form for common cases"""
    ensure_default_medications()
    
    if request.method == 'POST':
        form = QuickPrescriptionForm(request.POST, doctor=request.user)
        if form.is_valid():
            # Create prescription
            prescription = Prescription.objects.create(
                doctor=request.user,
                patient=form.cleaned_data['patient'],
                diagnosis=form.cleaned_data['diagnosis'],
                notes=form.cleaned_data.get('notes', ''),
                valid_until=timezone.now().date() + timedelta(days=30)
            )
            
            # Add medications
            for i in range(1, 4):
                medication = form.cleaned_data.get(f'medication_{i}')
                if medication:
                    PrescriptionItem.objects.create(
                        prescription=prescription,
                        medication=medication,
                        dosage=form.cleaned_data.get(f'dosage_{i}', '1 tablet'),
                        frequency=form.cleaned_data.get(f'frequency_{i}', 'twice_daily'),
                        duration_value=form.cleaned_data.get(f'duration_{i}', 7),
                        duration_unit='days',
                        quantity=form.cleaned_data.get(f'duration_{i}', 7) * 2  # Approximate quantity
                    )
            
            # Create history
            PrescriptionHistory.objects.create(
                prescription=prescription,
                action='created',
                performed_by=request.user
            )
            
            messages.success(request, f'Prescription {prescription.prescription_number} created.')
            return redirect('prescriptions:sign_prescription', pk=prescription.pk)
    else:
        form = QuickPrescriptionForm(doctor=request.user)
    
    return render(request, 'prescriptions/quick_prescription.html', {'form': form})


# ==================== PATIENT VIEWS ====================

@login_required
@patient_required
def my_prescriptions(request):
    """Patient view of their prescriptions"""
    prescriptions = Prescription.objects.filter(
        patient=request.user,
        status__in=['active', 'dispensed', 'completed']
    ).select_related('doctor').prefetch_related('items')
    
    # Filter by status
    status = request.GET.get('status')
    if status and status != 'all':
        prescriptions = prescriptions.filter(status=status)
    
    context = {
        'prescriptions': prescriptions,
        'status': status,
    }
    return render(request, 'prescriptions/patient_prescriptions.html', context)


@login_required
def view_prescription(request, pk):
    """Patient views a specific prescription"""
    prescription = get_object_or_404(Prescription, pk=pk)
    
    # Check access
    if request.user != prescription.patient and request.user != prescription.doctor:
        messages.error(request, 'You do not have access to this prescription.')
        return redirect('dashboard')
    
    # Record that patient viewed it
    if request.user == prescription.patient:
        if not prescription.history.filter(action='viewed').exists():
            PrescriptionHistory.objects.create(
                prescription=prescription,
                action='viewed',
                performed_by=request.user
            )
    
    context = {
        'prescription': prescription,
        'items': prescription.items.select_related('medication').all(),
        'is_patient': request.user == prescription.patient,
    }
    return render(request, 'prescriptions/view_prescription.html', context)


@login_required
def download_prescription(request, pk):
    """Generate PDF or printable version of prescription"""
    prescription = get_object_or_404(Prescription, pk=pk)
    
    # Check access
    if request.user != prescription.patient and request.user != prescription.doctor:
        messages.error(request, 'You do not have access to this prescription.')
        return redirect('dashboard')
    
    context = {
        'prescription': prescription,
        'items': prescription.items.select_related('medication').all(),
        'doctor_profile': prescription.doctor.doctorprofile if hasattr(prescription.doctor, 'doctorprofile') else None,
    }
    return render(request, 'prescriptions/prescription_print.html', context)


# ==================== API ENDPOINTS ====================

@login_required
def medication_search_api(request):
    """API for searching medications"""
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    medications = Medication.objects.filter(is_active=True)
    
    if query:
        medications = medications.filter(
            Q(name__icontains=query) |
            Q(generic_name__icontains=query)
        )
    
    if category:
        medications = medications.filter(category=category)
    
    data = [{
        'id': m.id,
        'name': str(m),
        'generic_name': m.generic_name,
        'form': m.get_form_display(),
        'category': m.get_category_display(),
    } for m in medications[:20]]
    
    return JsonResponse({'medications': data})


@login_required
@doctor_required
def prescription_stats(request):
    """Get prescription statistics for doctor dashboard"""
    doctor = request.user
    today = timezone.now().date()
    
    stats = {
        'total': Prescription.objects.filter(doctor=doctor).count(),
        'active': Prescription.objects.filter(doctor=doctor, status='active').count(),
        'this_month': Prescription.objects.filter(
            doctor=doctor,
            created_at__year=today.year,
            created_at__month=today.month
        ).count(),
        'pending_signature': Prescription.objects.filter(
            doctor=doctor,
            status='draft'
        ).count(),
    }
    
    return JsonResponse(stats)


# ==================== VERIFICATION VIEW ====================

def verify_prescription(request):
    """Public view to verify a prescription by number"""
    number = request.GET.get('number', '').strip()
    prescription = None
    verified = False
    
    if number:
        try:
            prescription = Prescription.objects.select_related('doctor', 'patient').prefetch_related('items__medication').get(
                prescription_number=number,
                status__in=['active', 'dispensed', 'completed']
            )
            verified = True
            
            # Log verification
            if request.user.is_authenticated:
                PrescriptionHistory.objects.create(
                    prescription=prescription,
                    action='verified',
                    performed_by=request.user,
                    notes=f'Verified by {request.user.username}'
                )
        except Prescription.DoesNotExist:
            verified = False
    
    context = {
        'number': number,
        'prescription': prescription,
        'verified': verified,
    }
    return render(request, 'prescriptions/verify_prescription.html', context)
