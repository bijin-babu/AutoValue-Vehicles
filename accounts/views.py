# from django.contrib.auth import login
# from django.contrib.auth.views import LoginView, LogoutView
# from django.shortcuts import render, redirect
# from django.urls import reverse_lazy
# from django.views.generic import CreateView, TemplateView
# from .forms import RegistrationForm

# class UserLoginView(LoginView):
#     template_name = 'accounts/login.html'
#     redirect_authenticated_user = True

#     def get_success_url(self):
#         user = self.request.user
#         if user.is_manager:
#             return reverse_lazy('manager_dashboard')
#         elif user.is_seller:
#             return reverse_lazy('seller_dashboard')
#         elif user.is_buyer:
#             return reverse_lazy('buyer_dashboard')
#         return reverse_lazy('home')

# def register_seller_view(request):
#     if request.user.is_authenticated:
#         return redirect('home')
        
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save_user(is_seller=True)
#             login(request, user)
#             return redirect('seller_dashboard')
#     else:
#         form = RegistrationForm()
#     return render(request, 'accounts/register.html', {'form': form, 'role': 'Seller'})

# def register_buyer_view(request):
#     if request.user.is_authenticated:
#         return redirect('home')
        
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save_user(is_buyer=True)
#             login(request, user)
#             return redirect('buyer_dashboard')
#     else:
#         form = RegistrationForm()
#     return render(request, 'accounts/register.html', {'form': form, 'role': 'Buyer'})

# class HomeView(TemplateView):
#     template_name = 'home.html'


from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from .forms import RegistrationForm


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.is_manager:
            return reverse_lazy("manager_dashboard")
        if user.is_seller:
            return reverse_lazy("seller_dashboard")
        if user.is_buyer:
            return reverse_lazy("buyer_dashboard")
        return reverse_lazy("home")


def register_seller_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save_user(is_seller=True)
            login(request, user)
            return redirect("seller_dashboard")
    else:
        form = RegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form, "role": "Seller"},
    )


def register_buyer_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save_user(is_buyer=True)
            login(request, user)
            return redirect("buyer_dashboard")
    else:
        form = RegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form, "role": "Buyer"},
    )


class HomeView(TemplateView):
    template_name = "home.html"