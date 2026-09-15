import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autovalue.settings')
django.setup()

from accounts.models import User
from vehicles.models import Vehicle, VehicleStatus

DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD")
if not DEMO_PASSWORD:
    raise RuntimeError("DEMO_PASSWORD environment variable is required.")

def run_seed():
    print("Seeding testing data...")
    try:
        seller = User.objects.create_user(
            email="seller@test.com", password=DEMO_PASSWORD,
            is_seller=True, full_name="Demo Seller", irish_mobile_number="0111234567"
        )
        print("Created Seller: seller@test.com")
    except Exception as e:
        print(f"Seller may already exist: {e}")
        seller = User.objects.filter(email='seller@test.com').first()

    try:
        buyer = User.objects.create_user(
            email="buyer@test.com", password=DEMO_PASSWORD,
            is_buyer=True, full_name="Demo Buyer", irish_mobile_number="0119876543"
        )
        print("Created Buyer: buyer@test.com")
    except Exception as e:
        print(f"Buyer may already exist: {e}")
        buyer = User.objects.filter(email='buyer@test.com').first()

    try:
        manager = User.objects.create_superuser(
            email="manager@test.com", password=DEMO_PASSWORD,
            full_name="Demo Manager"
        )
        print("Created Manager: manager@test.com")
    except Exception as e:
        print(f"Manager may already exist: {e}")

    # Dummy vehicle
    if not Vehicle.objects.filter(registration_number="123-D-00001").exists():
        Vehicle.objects.create(
            seller=seller, registration_number="123-D-00001", vehicle_type="Four-Wheeler",
            make="BMW", model="M3", colour="Blue", fuel_type="Petrol", kilometres_travelled=50000,
            seller_expected_price=45000, 
            house_number='1', street='High street', city='Dublin', county='D', eircode='A12BC34',
            status=VehicleStatus.SUBMITTED
        )
        print("Created dummy vehicle 123-D-00001 for Seller.")
    else:
        print("Dummy vehicle already exists.")

    print("Seeding complete.")

if __name__ == '__main__':
    run_seed()
