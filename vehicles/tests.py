from django.test import TestCase
from accounts.models import User
from accounts.forms import RegistrationForm
from django.core.files.uploadedfile import SimpleUploadedFile
from vehicles.models import Vehicle, VehicleStatus
from vehicles.forms import VehicleSubmissionForm
from decimal import Decimal
from vehicles.services.valuation import calculate_residual_value
from datetime import date

TEST_AUTH_VALUE = "TestVehiclePassword123!"
TEST_FORM_PASSWORD = "TestPassword123!"
class AutoValueTests(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            email='seller@test.com',
            password=TEST_AUTH_VALUE,
            full_name='Test Seller',
            irish_mobile_number='0871234567',
            is_seller=True
        )
        self.buyer = User.objects.create_user(
            email='buyer@test.com',
            password=TEST_AUTH_VALUE,
            full_name='Test Buyer',
            irish_mobile_number='0859876543',
            is_buyer=True
        )

    def test_seller_registration_validation(self):
        form_data = {
            'full_name': 'New Seller',
            'email': 'new@test.com',
            'irish_mobile_number': '12345678', # Invalid format
            'password': TEST_FORM_PASSWORD,
            'confirm_password': TEST_FORM_PASSWORD
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('irish_mobile_number', form.errors)

        form_data['irish_mobile_number'] = '0831112222' # Valid
        form2 = RegistrationForm(data=form_data)
        self.assertTrue(form2.is_valid())

    def test_buyer_registration_validation(self):
        form_data = {
            'full_name': 'New Buyer',
            'email': 'buyer@test.com', # Duplicate email
            'irish_mobile_number': '0831112222',
            'password': TEST_FORM_PASSWORD,
            'confirm_password': TEST_FORM_PASSWORD
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_vehicle_registration_validation(self):
        # Invalid reg number
        invalid_data = {
            'registration_number': 'INVALID-REG',
            'vehicle_type': 'Four-Wheeler',
            'model': 'Model S',
            'make': 'Tesla',
            'colour': 'Black',
            'fuel_type': 'Electric',
            'kilometres_travelled': 50000,
            'seller_expected_price': 30000,
            'house_number': '10',
            'street': 'Main St',
            'city': 'Dublin',
            'county': 'D',
            'eircode': 'D01AB12'
        }
        form = VehicleSubmissionForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('registration_number', form.errors)

        valid_data = invalid_data.copy()
        valid_data['registration_number'] = '151-D-12345'
        
        # Testing Duplicate validation
        Vehicle.objects.create(
            seller=self.seller, 
            registration_number='151-D-12345', 
            vehicle_type='Four-Wheeler',
            model='Model S',
            make='Tesla',
            colour='Black',
            fuel_type='Electric',
            kilometres_travelled=50000,
            seller_expected_price=30000,
            house_number='10',
            street='Main St',
            city='Dublin',
            county='D',
            eircode='D01AB12'
        )
        
        form_dup = VehicleSubmissionForm(data=valid_data)
        self.assertFalse(form_dup.is_valid())
        self.assertIn('request for this vehicle already exists', form_dup.errors['registration_number'][0])

    def test_residual_value_calculation(self):
        metrics = calculate_residual_value(
            on_road_price=Decimal('20000'),
            purchase_date=date.today().replace(year=date.today().year - 2), # 2 years ago = 24 months
            kilometres=40000
        )
        # AD = 70% of 20000 = 14000
        # adm = 14000/150 = 93.333
        # DCM = 24 * 93.333 = 2240
        # akm = 14000/200000 = 0.07
        # DCK = 40000 * 0.07 = 2800
        # TD = 5040
        # RV = 20000 - 5040 = 14960
        # RRV = 15000
        # final = 15000 * 0.95 = 14250
        
        self.assertEqual(metrics['assumed_depreciation'], Decimal('14000.00'))
        self.assertEqual(metrics['actual_months_used'], 24)
        self.assertEqual(metrics['residual_value'], Decimal('14960.00'))
        self.assertEqual(metrics['rounded_residual_value'], Decimal('15000.00'))
        self.assertEqual(metrics['final_price'], Decimal('14250.00'))
