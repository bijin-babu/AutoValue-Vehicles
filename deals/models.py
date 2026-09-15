from django.db import models
from accounts.models import User
from vehicles.models import Vehicle

class BuyerInterest(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='interests')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interests')
    interest_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('vehicle', 'buyer')

    def __str__(self):
        return f"{self.buyer.email} -> {self.vehicle.registration_number}"

class Deal(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name='deal')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deals')
    
    # Seller's bank details for transaction
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    iban = models.CharField(max_length=50, blank=True, null=True)
    bic = models.CharField(max_length=20, blank=True, null=True)

    # Progression flags
    seller_confirmed = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True)

    handover_confirmed = models.BooleanField(default=False)
    payment_transferred = models.BooleanField(default=False)
    transfer_date = models.DateTimeField(null=True, blank=True)
    
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    ownership_transferred_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Deal for {self.vehicle.registration_number}"
