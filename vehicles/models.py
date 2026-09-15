from django.db import models
from accounts.models import User

class VehicleStatus(models.TextChoices):
    SUBMITTED = 'Submitted', 'Submitted'
    REJECTED = 'Rejected', 'Rejected'
    APPROVED = 'Approved', 'Approved'
    VALUATION_COMPLETED = 'Valuation Completed', 'Valuation Completed'
    LISTED = 'Listed', 'Listed'
    INTEREST_RECEIVED = 'Interest Received', 'Interest Received'
    BUYER_SELECTED = 'Buyer Selected', 'Buyer Selected'
    DEAL_ACCEPTED = 'Deal Accepted', 'Deal Accepted'
    TRANSFERRED = 'Transferred', 'Transferred'
    OWNERSHIP_PENDING = 'Ownership Pending', 'Ownership Pending'
    OWNERSHIP_COMPLETED = 'Ownership Completed', 'Ownership Completed'

class Vehicle(models.fields.Field):
    pass # Wait, this should just be models.Model

class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('Two-Wheeler', 'Two-Wheeler'),
        ('Four-Wheeler', 'Four-Wheeler'),
    ]

    FUEL_TYPES = [
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid'),
    ]

    COUNTIES = [
        ('C', 'Cork'), ('CE', 'Clare'), ('CN', 'Cavan'), ('CW', 'Carlow'),
        ('D', 'Dublin'), ('DL', 'Donegal'), ('G', 'Galway'), ('KE', 'Kildare'),
        ('KK', 'Kilkenny'), ('KY', 'Kerry'), ('L', 'Limerick'), ('LD', 'Longford'),
        ('LH', 'Louth'), ('LM', 'Leitrim'), ('LS', 'Laois'), ('MH', 'Meath'),
        ('MN', 'Monaghan'), ('MO', 'Mayo'), ('OY', 'Offaly'), ('RN', 'Roscommon'),
        ('SO', 'Sligo'), ('T', 'Tipperary'), ('W', 'Waterford'), ('WH', 'Westmeath'),
        ('WX', 'Wexford'), ('WW', 'Wicklow')
    ]

    registration_number = models.CharField(max_length=20, primary_key=True, help_text="Format e.g. 231-D-12345")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    front_image = models.ImageField(upload_to='vehicles/front_images/')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    model = models.CharField(max_length=100)
    make = models.CharField(max_length=100)
    colour = models.CharField(max_length=50)
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPES)
    kilometres_travelled = models.PositiveIntegerField()
    seller_expected_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Address
    house_number = models.CharField(max_length=50)
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    county = models.CharField(max_length=2, choices=COUNTIES)
    eircode = models.CharField(max_length=10)

    status = models.CharField(max_length=30, choices=VehicleStatus.choices, default=VehicleStatus.SUBMITTED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.registration_number})"

class VehicleValuation(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name='valuation')
    on_road_price = models.DecimalField(max_digits=12, decimal_places=2)
    purchase_date = models.DateField()
    
    # Calculation fields
    assumed_depreciation = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    actual_months_used = models.IntegerField(null=True, blank=True)
    total_depreciation = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    residual_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    rounded_residual_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    final_system_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # Manager fields
    approved_listing_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Valuation for {self.vehicle.registration_number}"
