from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from users.models import DoctorProfile

def home(request):
    return render(request, 'healthlink/home.html')  # Keep original path

@login_required
def dashboard(request):
    return render(request, 'healthlink/users/dashboard.html')  # Keep original path

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    
    return render(request, 'healthlink/users/login.html', {'form': form})  

def logout_view(request):
    logout(request)
    return redirect('home')

# Placeholder views - ONLY keep these that don't conflict with appointments app
def patient_register(request):
    # Use your actual patient registration template if it exists
    return render(request, 'healthlink/users/patient_register.html', {
        'title': 'Patient Registration'
    })

def doctor_register(request):
    if request.method == 'POST':
        return redirect('login')
    
    # Show the registration form for GET requests
    return render(request, 'healthlink/users/doctor_register.html', {
        'title': 'Doctor Registration'
    })

@login_required
def profile(request):
    # Use your actual profile template if it exists
    return render(request, 'healthlink/users/profile.html', {
        'title': 'User Profile'
    })

def doctor_list(request):
    doctors = DoctorProfile.objects.select_related('user').all()
    return render(request, 'healthlink/doctor_list.html', {'doctors': doctors})

def patient_register(request):
    if request.method == 'POST':
        return redirect('login')
    
    # Show the registration form for GET requests
    return render(request, 'healthlink/users/patient_register.html', {
        'title': 'Patient Registration'
    })