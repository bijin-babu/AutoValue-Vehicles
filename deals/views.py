from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from vehicles.models import Vehicle, VehicleStatus
from .models import BuyerInterest, Deal
from django.db.models import Q
from datetime import date
from dateutil.relativedelta import relativedelta

def is_buyer(user):
    return getattr(user, 'is_buyer', False)

@login_required
@user_passes_test(is_buyer)
def buyer_dashboard(request):
    vehicles = Vehicle.objects.filter(status__in=[VehicleStatus.LISTED, VehicleStatus.INTEREST_RECEIVED]).order_by('-updated_at')
    
    # Simple filtering logic
    county = request.GET.get('county')
    vehicle_type = request.GET.get('vehicle_type')
    fuel_type = request.GET.get('fuel_type')
    max_price = request.GET.get('max_price')

    if county:
        vehicles = vehicles.filter(county=county)
    if vehicle_type:
        vehicles = vehicles.filter(vehicle_type=vehicle_type)
    if fuel_type:
        vehicles = vehicles.filter(fuel_type=fuel_type)
    if max_price:
        vehicles = vehicles.filter(valuation__approved_listing_price__lte=max_price)

    # Context to see what they have already shown interest in
    user_interests = BuyerInterest.objects.filter(buyer=request.user).values_list('vehicle_id', flat=True)

    return render(request, 'deals/buyer_dashboard.html', {
        'vehicles': vehicles,
        'user_interests': user_interests
    })

@login_required
@user_passes_test(is_buyer)
def express_interest(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    
    if request.method == 'POST':
        # Prevent duplicates
        interest, created = BuyerInterest.objects.get_or_create(vehicle=vehicle, buyer=request.user)
        if created:
            if vehicle.status == VehicleStatus.LISTED:
                vehicle.status = VehicleStatus.INTEREST_RECEIVED
                vehicle.save()
            messages.success(request, f"You expressed interest in {vehicle.registration_number}. A manager will contact you soon.")
        else:
            messages.info(request, "You have already expressed interest in this vehicle.")
            
    return redirect('buyer_dashboard')

# DEAL SELECTION (Manager)
def is_manager(user):
    return getattr(user, 'is_manager', False)

@login_required
@user_passes_test(is_manager)
def manager_deals_dashboard(request):
    # Vehicles with interest received
    vehicles_interest = Vehicle.objects.filter(status=VehicleStatus.INTEREST_RECEIVED)
    deals_in_progress = Vehicle.objects.filter(status__in=[VehicleStatus.BUYER_SELECTED, VehicleStatus.DEAL_ACCEPTED, VehicleStatus.TRANSFERRED])
    
    return render(request, 'deals/manager_deals_dashboard.html', {
        'vehicles_interest': vehicles_interest,
        'deals_in_progress': deals_in_progress
    })

@login_required
@user_passes_test(is_manager)
def manager_select_buyer(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    interests = BuyerInterest.objects.filter(vehicle=vehicle)

    if request.method == 'POST':
        buyer_id = request.POST.get('buyer_id')
        if buyer_id:
            from accounts.models import User
            selected_buyer = get_object_or_404(User, pk=buyer_id)
            
            # Create the Deal object
            deal, created = Deal.objects.get_or_create(vehicle=vehicle, buyer=selected_buyer)
            vehicle.status = VehicleStatus.BUYER_SELECTED
            vehicle.save()
            messages.success(request, f"Buyer {selected_buyer.full_name} selected. Seller notified.")
            return redirect('manager_deals_dashboard')

    return render(request, 'deals/manager_select_buyer.html', {'vehicle': vehicle, 'interests': interests})

# SELLER CONFIRMATION
def is_seller(user):
    return getattr(user, 'is_seller', False)

@login_required
@user_passes_test(is_seller)
def seller_deal_confirmation(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, seller=request.user)
    if not hasattr(vehicle, 'deal'):
        messages.error(request, "No deal assigned yet.")
        return redirect('seller_dashboard')
        
    deal = vehicle.deal
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            bank_name = request.POST.get('bank_name')
            iban = request.POST.get('iban')
            bic = request.POST.get('bic')
            
            deal.bank_name = bank_name
            deal.iban = iban
            deal.bic = bic
            deal.seller_confirmed = True
            deal.save()
            
            vehicle.status = VehicleStatus.DEAL_ACCEPTED
            vehicle.save()
            messages.success(request, "Deal accepted. Bank details saved securely.")
            return redirect('seller_dashboard')
            
        elif action == 'reject':
            reason = request.POST.get('rejection_reason')
            deal.rejection_reason = reason
            deal.seller_confirmed = False
            deal.save()
            
            # Reset vehicle to LISTED so another buyer might show interest
            vehicle.status = VehicleStatus.LISTED
            vehicle.save()
            
            # Depending on business logic, we could delete the deal entirely
            # I think it's better to nuke the deal so the DB doesn't get cluttered with rejected deals
            deal.delete()
            messages.info(request, "Deal rejected. Vehicle is back to Listed status.")
            return redirect('seller_dashboard')

    return render(request, 'deals/seller_confirmation.html', {'vehicle': vehicle, 'deal': deal})

# MANAGER HANDOVER
@login_required
@user_passes_test(is_manager)
def manager_process_handover(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if not hasattr(vehicle, 'deal'):
        return redirect('manager_deals_dashboard')
        
    deal = vehicle.deal
    
    if request.method == 'POST':
        deal.handover_confirmed = True
        deal.payment_transferred = True
        deal.transfer_date = date.today()
        deal.ownership_transferred_date = date.today() + relativedelta(days=40)
        deal.amount_paid = vehicle.valuation.approved_listing_price
        deal.save()
        
        vehicle.status = VehicleStatus.TRANSFERRED
        vehicle.save()
        messages.success(request, "Handover and payment confirmed. Ownership pending for 40 days.")
        return redirect('manager_deals_dashboard')
        
    return render(request, 'deals/manager_handover.html', {'vehicle': vehicle, 'deal': deal})

