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

def OTP(req):
    digits = "0123456789"
    OTP = ""
    for i in range(6) :
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

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

        messages.success(req, "OTP sent! Check your email.")
        return redirect("validate_otp")  # Redirect to OTP validation page

    return render(req, 'register.html')

def validate(req,name,password,email,otp):
    if req.method=='POST':
        uotp=req.POST['uotp']
        if uotp==otp:
            data=User.objects.create_user(first_name=name,email=email,password=password,username=email)
            data.save()
            messages.success(req, "OTP verified successfully. You can now log in.")
            return redirect(rent_login)
        else:
            messages.error(req, "Invalid OTP. Please try again.")
            return redirect("validate",name=name,password=password,email=email,otp=otp)
    else:
        return render(req,'validate.html',{'name':name,'pass':password,'email':email,'otp':otp})

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

@staff_member_required
def update_visit_status(request, id, status):
    visit_request = get_object_or_404(VisitRequest, id=id)
    visit_request.status = status
    visit_request.save()

    # Get the user's email from the User model
    user_email = visit_request.user.email  # ✅ Use visit_request.user.email if user is linked

    # Send email
    from django.core.mail import send_mail
    send_mail(
        subject="Visit Request Status Update",
        message=f"Dear {visit_request.user_name}, your visit request has been {status}.",
        from_email='electronicera0124@gmail.com',  # Replace with your admin email
        recipient_list=[user_email],  # Use correct email field
        fail_silently=False,
    )

    messages.success(request, f"Visit request has been {status} and email sent!")
    return redirect('manage_visit_requests')




# ___________________________User_____________________________

def user_home(req):
    houses=House.objects.all()
    return render(req,'user/home.html',{'houses':houses})

def house_detail(request,id):
    house = get_object_or_404(House, id=id)
    return render(request, 'user/house_detail.html', {'house': house})

# def visit(req,id):
#     house = get_object_or_404(House, id=id)
#     if req.method == 'POST':
#         user_name=req.POST['user_name']
#         phone_number=req.POST['phone_number']
#         time_slot=req.POST['time_slot']
#         data=VisitRequest.objects.create(user_name=user_name,phone_number=phone_number,time_slot=time_slot)
#         data.save()
#     return render(req,'user/visit.html',{'house':house})


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

