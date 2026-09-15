from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Vehicle, VehicleStatus, VehicleValuation
from .forms import VehicleSubmissionForm
from decimal import Decimal
from .services.valuation import calculate_residual_value
from datetime import datetime
from django.contrib import messages
from .models import Vehicle, VehicleStatus, VehicleValuation
from .forms import VehicleSubmissionForm

@login_required
def seller_dashboard(request):
    if not getattr(request.user, 'is_seller', False):
        messages.error(request, "Access Denied. Seller only area.")
        return redirect('home')
        
    vehicles = Vehicle.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'vehicles/seller_dashboard.html', {'vehicles': vehicles})

@login_required
def submit_vehicle(request):
    if not getattr(request.user, 'is_seller', False):
        messages.error(request, "Access Denied.")
        return redirect('home')

    if request.method == 'POST':
        form = VehicleSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.seller = request.user
            vehicle.status = VehicleStatus.SUBMITTED
            vehicle.save()
            # Dev Note: We need to figure out if we want to add an email notification here later
            messages.success(request, "Vehicle submitted successfully.")
            return redirect('seller_dashboard')
    else:
        # Just render the blank form for first-time visitors
        form = VehicleSubmissionForm()

    return render(request, 'vehicles/submit_vehicle.html', {'form': form})

@login_required
def edit_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, seller=request.user)
    
    # Only allow editing if it hasn't been processed by a manager yet
    if vehicle.status != VehicleStatus.SUBMITTED:
        messages.error(request, "You can no longer edit this vehicle as it is out of the Submitted state.")
        return redirect('seller_dashboard')

    if request.method == 'POST':
        form = VehicleSubmissionForm(request.POST, request.FILES, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, "Vehicle updated successfully.")
            return redirect('seller_dashboard')
    else:
        form = VehicleSubmissionForm(instance=vehicle)

    return render(request, 'vehicles/edit_vehicle.html', {'form': form, 'vehicle': vehicle})

@login_required
def delete_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, seller=request.user)
    
    if vehicle.status != VehicleStatus.SUBMITTED:
        messages.error(request, "You can only delete vehicles that are in the Submitted state.")
        return redirect('seller_dashboard')

    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, "Vehicle deleted successfully.")
        return redirect('seller_dashboard')

    return render(request, 'vehicles/delete_vehicle.html', {'vehicle': vehicle})

# MANAGER VIEWS
def is_manager(user):
    return getattr(user, 'is_manager', False)

@login_required
@user_passes_test(is_manager)
def manager_dashboard(request):
    submitted_vehicles = Vehicle.objects.filter(status=VehicleStatus.SUBMITTED).order_by('created_at')
    valuation_completed = Vehicle.objects.filter(status__in=[VehicleStatus.VALUATION_COMPLETED, VehicleStatus.LISTED]).order_by('-updated_at')
    
    context = {
        'submitted_vehicles': submitted_vehicles,
        'valuation_completed': valuation_completed
    }
    return render(request, 'vehicles/manager_dashboard.html', context)

@login_required
@user_passes_test(is_manager)
def manager_review(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'reject':
            # Simplified rejection: set reason and reject
            # TODO: Maybe we should add a text field for managers to give a reason to the seller
            vehicle.status = VehicleStatus.REJECTED
            vehicle.save()
            messages.info(request, "Vehicle Request Rejected.")
            return redirect('manager_dashboard')
            
        elif action == 'approve_valuate':
            on_road_price = request.POST.get('on_road_price')
            purchase_date_str = request.POST.get('purchase_date')
            
            if on_road_price and purchase_date_str:
                p_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date()
                
                # Call Microservice-equivalent calculation
                metrics = calculate_residual_value(
                    on_road_price=Decimal(on_road_price),
                    purchase_date=p_date,
                    kilometres=vehicle.kilometres_travelled
                )
                
                # Save valuation
                VehicleValuation.objects.create(
                    vehicle=vehicle,
                    on_road_price=on_road_price,
                    purchase_date=p_date,
                    assumed_depreciation=metrics['assumed_depreciation'],
                    actual_months_used=metrics['actual_months_used'],
                    total_depreciation=metrics['total_depreciation'],
                    residual_value=metrics['residual_value'],
                    rounded_residual_value=metrics['rounded_residual_value'],
                    final_system_price=metrics['final_price']
                )
                
                vehicle.status = VehicleStatus.VALUATION_COMPLETED
                vehicle.save()
                messages.success(request, "Vehicle Valuated successfully.")
                return redirect('manager_dashboard')
            else:
                messages.error(request, "Please enter all valuation fields.")
                
    return render(request, 'vehicles/manager_review.html', {'vehicle': vehicle})

@login_required
@user_passes_test(is_manager)
def manager_list_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'list':
            list_price = request.POST.get('approved_listing_price')
            if list_price:
                vehicle.valuation.approved_listing_price = Decimal(list_price)
                vehicle.valuation.save()
                vehicle.status = VehicleStatus.LISTED
                vehicle.save()
                messages.success(request, f"Vehicle {vehicle.registration_number} listed for {list_price} Euro.")
                return redirect('manager_dashboard')
            else:
                messages.error(request, "Please enter an approved listing price.")
                
    return render(request, 'vehicles/manager_list_vehicle.html', {'vehicle': vehicle})

