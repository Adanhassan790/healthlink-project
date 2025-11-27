from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json
from .models import MpesaTransaction, Appointment
from .mpesa_service import initiate_stk_push

@login_required
def payment_page(request, appointment_id):
    """Display payment page for an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    
    # Check if appointment already has a successful payment
    successful_payment = MpesaTransaction.objects.filter(
        appointment=appointment, 
        status='success'
    ).first()
    
    if successful_payment:
        messages.info(request, 'This appointment has already been paid for.')
        return redirect('appointment_detail', appointment_id=appointment_id)
    
    context = {
        'appointment': appointment,
        'doctor': appointment.doctor.doctorprofile,
        'amount': appointment.doctor.doctorprofile.consultation_fee,
    }
    
    return render(request, 'payments/payment.html', context)

@login_required
def initiate_payment(request, appointment_id):
    """Initiate M-Pesa STK Push payment"""
    if request.method == 'POST':
        appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
        
        # Get phone number from form
        phone_number = request.POST.get('phone_number')
        amount = appointment.doctor.doctorprofile.consultation_fee
        
        if not phone_number:
            return JsonResponse({
                'success': False,
                'message': 'Phone number is required'
            })
        
        # Initiate STK Push
        transaction, message = initiate_stk_push(phone_number, amount, appointment)
        
        if transaction:
            return JsonResponse({
                'success': True,
                'message': message,
                'transaction_id': transaction.id,
                'checkout_request_id': transaction.checkout_request_id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': message
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

@csrf_exempt
def mpesa_callback(request):
    """Handle M-Pesa payment callback"""
    if request.method == 'POST':
        try:
            callback_data = json.loads(request.body)
            
            # Extract callback metadata
            stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            
            # Find transaction
            transaction = MpesaTransaction.objects.get(
                checkout_request_id=checkout_request_id
            )
            
            # Update transaction status
            transaction.result_code = result_code
            transaction.result_description = result_desc
            
            if result_code == 0:
                # Payment successful
                transaction.status = 'success'
                
                # Extract receipt number and other details
                callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                for item in callback_metadata:
                    if item.get('Name') == 'MpesaReceiptNumber':
                        transaction.mpesa_receipt_number = item.get('Value')
                    elif item.get('Name') == 'TransactionDate':
                        transaction.transaction_date = item.get('Value')
                
                # Update appointment status
                transaction.appointment.status = 'confirmed'
                transaction.appointment.save()
                
            else:
                # Payment failed
                transaction.status = 'failed'
            
            transaction.save()
            
            # Return success response to M-Pesa
            return JsonResponse({
                "ResultCode": 0,
                "ResultDesc": "Success"
            })
            
        except Exception as e:
            print(f"Error processing callback: {e}")
            return JsonResponse({
                "ResultCode": 1,
                "ResultDesc": "Failed"
            })
    
    return JsonResponse({
        "ResultCode": 1,
        "ResultDesc": "Invalid request"
    })

@login_required
def payment_status(request, transaction_id):
    """Check payment status"""
    transaction = get_object_or_404(MpesaTransaction, id=transaction_id, user=request.user)
    
    return JsonResponse({
        'status': transaction.status,
        'receipt_number': transaction.mpesa_receipt_number,
        'result_description': transaction.result_description
    })