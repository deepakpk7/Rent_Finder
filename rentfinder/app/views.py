from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .models import *
import os
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import math,random
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.validators import validate_email
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
import re
from .models import VisitRequest
from django.contrib.admin.views.decorators import staff_member_required


# Create your views here.

def rent_login(req):
    if 'admin' in req.session:
            return redirect(admin_home)
    if 'user' in req.session:
        return redirect(user_home)
    if req.method=='POST':
        uname=req.POST['uname']
        password=req.POST['password']
        shop=authenticate(username=uname,password=password)
        if shop:
                login(req,shop)
                if shop.is_superuser:
                        req.session['admin']=uname   
                        return redirect(admin_home)
                else:
                        req.session['user']=uname   
                        return redirect(user_home)
        else:
            messages.warning(req,'Invaild username or password!!!')
            return redirect(rent_login)
    else:
        return render(req,'login.html')

def generate_otp():
    return ''.join(random.choices("0123456789", k=6))

def register(req):
    if req.method == 'POST':
        email = req.POST.get('email', '').strip()
        name = req.POST.get('uname', '').strip()
        password = req.POST.get('password', '')

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(req, "Invalid email format.")
            return redirect("register")

        # Check if email is already registered
        if User.objects.filter(email=email).exists():
            messages.error(req, "Email is already in use.")
            return redirect("register")

        # Validate password strength (min 8 chars, at least one digit, one special char)
        if len(password) < 8 or not re.search(r"\d", password) or not re.search(r"\W", password):
            messages.error(req, "Password must be at least 8 characters long, contain a number and a special character.")
            return redirect("register")

        # Generate OTP
        otp = generate_otp()

        # Store user details and OTP in session (temporary storage)
        req.session['register_data'] = {
            'email': email,
            'name': name,
            'password': password,
            'otp': otp
        }

        # Send OTP via email
        subject = "Your OTP for Account Registration"
        message = f"Hello {name},\n\nYour OTP for verification is: {otp}.\n\nBest Regards,\nYour Website Team"
        sender_email = settings.EMAIL_HOST_USER
        send_mail(subject, message, sender_email, [email])

        messages.success(req, "OTP sent! Check your email.")
        return redirect("validate_otp")  # Redirect to OTP validation page

    return render(req, 'register.html')

def validate_otp(req):
    if req.method == 'POST':
        user_otp = req.POST.get('user_otp', '').strip()
        register_data = req.session.get('register_data', {})

        # Check if session data exists
        if not register_data:
            messages.error(req, "Session expired! Please register again.")
            return redirect("register")

        # Extract user data
        name = register_data.get('name')
        email = register_data.get('email')
        password = register_data.get('password')
        otp = register_data.get('otp')

        if user_otp == otp:
            # Create User
            user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
            user.save()

            messages.success(req, "OTP verified successfully. You can now log in.")
            return redirect(rent_login)  # Redirect to login page
        else:
            messages.error(req, "Invalid OTP. Please try again.")
            return redirect("validate_otp")  # Stay on OTP page

    return render(req, 'validate.html')


def rent_logout(req):
    logout(req)
    req.session.flush()
    return redirect(user_home)


# ___________________________Admin___________________________

def admin_home(req):
    if 'admin' in req.session:
        data=House.objects.all()
        data2 = VisitRequest.objects.all().order_by('-requested_at')  # Newest first
        return render(req,'admin/admin_home.html',{'data':data,'data2':data2})
    else:
        return redirect(rent_login)
    

def add_house(request):
    if request.method == 'POST':
        form = HouseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(admin_home)  # Redirect to the house list page
    else:
        form = HouseForm()
    
    return render(request, 'admin/add_house.html', {'form': form})

def edit_house(request,id):
    house = get_object_or_404(House, id=id)  # Get the house or return 404

    if request.method == 'POST':
        form = HouseForm(request.POST, request.FILES, instance=house)
        if form.is_valid():
            form.save()
            return redirect('house_list')  # Redirect to house list after saving
    else:
        form = HouseForm(instance=house)

    return render(request, 'admin/edit_house.html', {'form': form, 'house': house})


# Delete House View
def delete_house(request, id):
    house = get_object_or_404(House, id=id)
    house.delete()
    return redirect(admin_home)

# Admin View to Approve or Reject Requests
@staff_member_required
def manage_visit_requests(request):
    visit_requests = VisitRequest.objects.filter(status='pending')
    return render(request, 'admin/visit_requests.html', {'visit_requests': visit_requests})

def update_visit_status(request, id, status):
    visit_request = get_object_or_404(VisitRequest, id=id)
    visit_request.status = status
    visit_request.save()

    subject = ""
    message = ""
    
    if status == 'approved':
        subject = "Your House Visit Request Has Been Approved!"
        message = f"Hello {visit_request.user.username},\n\nYour house visit request for {visit_request.house.title} has been approved.\n\nThank you for using our service!\n\nBest Regards,\nAdmin Team"
    else:
        subject = "Your House Visit Request Has Been Rejected!"
        message = f"Hello {visit_request.user.username},\n\nUnfortunately, your house visit request for {visit_request.house.title} has been rejected.\n\nThank you for using our service!\n\nBest Regards,\nAdmin Team"

    recipient_email = visit_request.user.email
    print(recipient_email)
    sender_email = settings.EMAIL_HOST_USER
    send_mail(subject, message, sender_email, [recipient_email])
    

    try:
        send_mail(subject, message, sender_email, [recipient_email], fail_silently=False)
        messages.success(request, f"Visit request has been {status} and email sent successfully!")
    except Exception as e:
        messages.error(request, f"Error sending email: {e}")
    
    return redirect('manage_visit_requests')




# ___________________________User_____________________________

def user_home(req):
    houses=House.objects.all()
    return render(req,'user/home.html',{'houses':houses})

def house_detail(request,id):
    house = get_object_or_404(House, id=id)
    return render(request, 'user/house_detail.html', {'house': house})

# @login_required
def profile(req):
    if 'user' in req.session:
        visit_requests = VisitRequest.objects.filter(user=req.user).order_by('-id')  # Fetch user's visit requests
        return render(req,'user/profile.html', {'visit_requests': visit_requests})
    else:
        return redirect(rent_login)

def update_profile(req):
    if req.method == "POST":
        new_first_name = req.POST.get("name")
        new_username = req.POST.get("username")

        if User.objects.filter(username=new_username).exclude(id=req.user.id).exists():
            messages.error(req, "This username is already taken. Please choose another one.")
            return redirect(profile) 

        
        if new_first_name and new_username:
            req.user.first_name = new_first_name
            req.user.username = new_username
            req.user.save()
            messages.success(req, "Username updated successfully!")
        else:
            messages.error(req, "Username and Name cannot be empty.")
    return redirect(profile)

def visit(request, id):
    if 'user' in request.session:
        house = get_object_or_404(House, id=id)  # Get the house object

        if request.method == 'POST':
            user_name = request.POST.get('user_name')
            phone_number = request.POST.get('phone_number')
            time_slot = request.POST.get('time_slot')

            # Ensure all fields are filled
            if not user_name or not phone_number or not time_slot:
                messages.error(request, "All fields are required!")
                return render(request, 'user/visit.html', {'house': house})

            # Create visit request with house field
            visit_request = VisitRequest.objects.create(
                house=house,  # Assign the house
                user=request.user if request.user.is_authenticated else None,  # Assign user if logged in
                user_name=user_name,
                phone_number=phone_number,
                time_slot=time_slot
            )
            visit_request.save()
            
            messages.success(request, "Your visit request has been submitted successfully!")
            return redirect('house_detail', id=id)  # Redirect to house detail page
        return render(request, 'user/visit.html', {'house': house})
    else:
        return redirect(rent_login)  # Redirect to login page if user is not logged in


def schedule_visit(request, house_id):
    house = get_object_or_404(House, id=house_id)

    if request.method == "POST":
        form = VisitRequestForm(request.POST)
        if form.is_valid():
            visit_request = form.save(commit=False)
            visit_request.house = house
            if request.user.is_authenticated:
                visit_request.user = request.user
            visit_request.save()
            messages.success(request, "Your visit request has been submitted for approval!")
            return redirect('house_detail', house_id=house.id)
        else:
            messages.error(request, "Please correct the errors below.")

    return redirect('house_detail', house_id=house.id)

