from django import forms
from .models import Vehicle
import re
from django.core.exceptions import ValidationError

class VehicleSubmissionForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        exclude = ['seller', 'status']
    
    def clean_registration_number(self):
        reg_num = self.cleaned_data.get('registration_number', '')
        # Pattern e.g. 231-D-12345 or 12-KE-123
        pattern = r"^\d{2,3}-[A-Z]{1,2}-\d{1,6}$"
        if not bool(re.match(pattern, reg_num)):
            raise ValidationError("Must follow Irish registration style like 231-D-12345 (numeric-letter-numeric grouping).")
        
        # Prevent duplicates
        # Exclude the current instance so we can edit existing vehicles
        if Vehicle.objects.filter(registration_number=reg_num).exclude(pk=self.instance.pk).exists():
            raise ValidationError("A request for this vehicle already exists.")
            
        return reg_num
