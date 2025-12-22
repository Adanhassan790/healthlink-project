from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def patient_required(view_func):
    """
    Decorator that ensures the user is a patient.
    Redirects doctors to their dashboard with a message.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if request.user.user_type != 'patient':
            messages.warning(request, 'This feature is only available for patients.')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def doctor_required(view_func):
    """
    Decorator that ensures the user is a doctor.
    Redirects patients to their dashboard with a message.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if request.user.user_type != 'doctor':
            messages.warning(request, 'This feature is only available for doctors.')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def staff_required(view_func):
    """
    Decorator that ensures the user is staff/admin.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_staff:
            messages.warning(request, 'This feature is only available for staff members.')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper
