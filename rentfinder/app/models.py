from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class House(models.Model):
    PROPERTY_TYPES = [
        ('apartment', 'Apartment'),
        ('flat', 'Flat'),
        ('house', 'House'),
        ('pg', 'PG'),
    ]
    
    BHK_CHOICES = [
        ('1RK', '1 RK'),
        ('1BHK', '1 BHK'),
        ('2BHK', '2 BHK'),
        ('3BHK', '3 BHK'),
        ('4BHK', '4 BHK'),
    ]
    
    PREFERRED_TENANTS = [
        ('boys', 'Boys'),
        ('girls', 'Girls'),
        ('couples', 'Couples'),
        ('family', 'Family'),
        ('mixed', 'Mixed'),
        ('unmarried_couples', 'Unmarried Couples'),
    ]
    
    LOOKING_FOR_CHOICES = [
        ('students', 'Students'),
        ('working_professionals', 'Working Professionals'),
        ('family', 'Family'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    location = models.CharField(max_length=200)
    image = models.ImageField(blank=True, null=True)
    
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    bhk_type = models.CharField(max_length=10, choices=BHK_CHOICES, default='1RK')
    
    preferred_tenants = models.CharField(max_length=20, choices=PREFERRED_TENANTS)
    looking_for = models.CharField(max_length=30, choices=LOOKING_FOR_CHOICES)
    
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    furnishing = models.CharField(max_length=50, choices=[('semi-furnished', 'Semi-Furnished'), ('fully-furnished', 'Fully-Furnished'), ('unfurnished', 'Unfurnished')])
    
    rating = models.FloatField(default=0.0)
    available_from = models.DateField()

    def __str__(self):
        return f"{self.title} - {self.location}"


class VisitRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    house = models.ForeignKey('House', on_delete=models.CASCADE, related_name="visit_requests")
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    user_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    time_slot = models.CharField(max_length=50)
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')