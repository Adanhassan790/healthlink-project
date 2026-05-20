from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Sum
import json
from django.conf import settings
from .models import MpesaTransaction, Appointment
from .mpesa_service import initiate_stk_push


@login_required
def payment_history(request):
    """Display payment history for the user"""
    transactions = MpesaTransaction.objects.filter(user=request.user).order_by('-created_at')
    
    # Calculate totals
    successful_transactions = transactions.filter(status='success')
    total_paid = successful_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    total_transactions = transactions.count()
    successful_count = successful_transactions.count()
    
    context = {
        'transactions': transactions,
        'total_paid': total_paid,
        'total_transactions': total_transactions,
        'successful_count': successful_count,
    }
    return render(request, 'payments/payment_history.html', context)

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
        'ENABLE_PAYMENT_SIMULATION': getattr(settings, 'ENABLE_PAYMENT_SIMULATION', settings.DEBUG),
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
    print("=" * 50)
    print("📞 M-PESA CALLBACK RECEIVED")
    print(f"📅 Time: {timezone.now()}")
    print(f"📝 Method: {request.method}")
    
    if request.method == 'POST':
        try:
            # Log raw body
            raw_body = request.body.decode('utf-8')
            print(f"📦 Raw Body: {raw_body}")
            
            callback_data = json.loads(raw_body)
            print(f"📋 Parsed Data: {json.dumps(callback_data, indent=2)}")
            
            # Extract callback metadata
            stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            
            print(f"🔑 CheckoutRequestID: {checkout_request_id}")
            print(f"📊 ResultCode: {result_code}")
            print(f"📝 ResultDesc: {result_desc}")
            
            # Find transaction
            try:
                transaction = MpesaTransaction.objects.get(
                    checkout_request_id=checkout_request_id
                )
                print(f"✅ Found transaction: {transaction.id}")
            except MpesaTransaction.DoesNotExist:
                print(f"❌ Transaction not found for CheckoutRequestID: {checkout_request_id}")
                return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
            
            # Update transaction status
            transaction.result_code = result_code
            transaction.result_description = result_desc
            
            if str(result_code) == '0':
                # Payment successful
                transaction.status = 'success'
                print("✅ Payment SUCCESSFUL!")
                
                # Extract receipt number and other details
                callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                for item in callback_metadata:
                    if item.get('Name') == 'MpesaReceiptNumber':
                        transaction.mpesa_receipt_number = item.get('Value')
                        print(f"🧾 Receipt: {transaction.mpesa_receipt_number}")
                    elif item.get('Name') == 'TransactionDate':
                        transaction.transaction_date = item.get('Value')
                    elif item.get('Name') == 'Amount':
                        print(f"💰 Amount: {item.get('Value')}")
                    elif item.get('Name') == 'PhoneNumber':
                        print(f"📱 Phone: {item.get('Value')}")
                
                # Update appointment status
                transaction.appointment.status = 'confirmed'
                transaction.appointment.save()
                print(f"📅 Appointment {transaction.appointment.id} confirmed!")
                
            else:
                # Payment failed or cancelled
                transaction.status = 'failed'
                print(f"❌ Payment FAILED: {result_desc}")
            
            transaction.save()
            print(f"💾 Transaction saved with status: {transaction.status}")
            print("=" * 50)
            
            # Return success response to M-Pesa
            return JsonResponse({
                "ResultCode": 0,
                "ResultDesc": "Success"
            })
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {e}")
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
            
        except Exception as e:
            print(f"❌ Error processing callback: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                "ResultCode": 0,
                "ResultDesc": "Accepted"
            })
    
    print("❌ Invalid request method")
    return JsonResponse({
        "ResultCode": 0,
        "ResultDesc": "Accepted"
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


# ADD THIS FUNCTION TO YOUR VIEWS.PY
@login_required
def simulate_payment(request, appointment_id):
    """Simulate payment for development/testing with any phone number"""
    if not getattr(settings, 'ENABLE_PAYMENT_SIMULATION', settings.DEBUG):
        messages.error(request, 'Payment simulation is disabled in this environment.')
        return redirect('payments:payment_page', appointment_id=appointment_id)

    if request.method == 'POST':
        appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
        
        # Get phone number from form
        phone_number = request.POST.get('phone_number')
        amount = appointment.doctor.doctorprofile.consultation_fee
        
        if not phone_number:
            messages.error(request, 'Phone number is required')
            return redirect('payment_page', appointment_id=appointment_id)
        
        # Format phone number
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif phone_number.startswith('+'):
            phone_number = phone_number[1:]
        
        # Create a simulated transaction (SUCCESS)
        transaction = MpesaTransaction.objects.create(
            appointment=appointment,
            user=request.user,
            amount=amount,
            phone_number=phone_number,
            checkout_request_id=f"SIM_{random.randint(10000, 99999)}",
            merchant_request_id=f"SIM_{random.randint(10000, 99999)}",
            mpesa_receipt_number=f"SIM{random.randint(100000, 999999)}",
            status='success',
            result_code=0,
            result_description="Simulated payment successful",
            transaction_date=timezone.now()
        )
        
        # Update appointment status
        appointment.status = 'confirmed'
        appointment.save()
        
        messages.success(request, f'Payment simulated successfully! Receipt: {transaction.mpesa_receipt_number}')
        return redirect('appointments:my_appointments')
    
    return redirect('payment_page', appointment_id=appointment_id)