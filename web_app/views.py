from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views import View
from web_app import models as m
from web_app import forms as f


class BaseView(View):
    def get(self, request):
        return render(request, 'base.html')


class PlansView(View):
    def get(self, request):
        plans_list = m.Plans.objects.all().order_by('date_created')
        paginator = Paginator(plans_list, 10)
        page = request.GET.get('page')
        plans = paginator.get_page(page)
        return render(request, 'plans.html', {'plans': plans})


class MealsView(View):
    def get(self, request):
        meals_list = m.Meals.objects.all().order_by('date_created')
        paginator = Paginator(meals_list, 10)
        page = request.GET.get('page')
        meals = paginator.get_page(page)
        return render(request, 'meals.html', {'meals': meals})


class ProductsView(View):
    def get(self, request):
        products_list = m.Products.objects.all().order_by('type__products')
        paginator = Paginator(products_list, 10)
        page = request.GET.get('page')
        products = paginator.get_page(page)
        return render(request, 'products.html', {'products': products})


class LoginView(View):
    def get(self, request):
        form = f.LoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = f.LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = data.get('username')
            password = data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('/')
            else:
                msg = 'Podano nieprawidłowe dane logowania.'
                return render(request, 'login.html', {'form': form, 'msg': msg})
        else:
            return render(request, 'login.html', {'form': form})


class UserCreateView(View):
    def get(self, request):
        form = f.UserCreateForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = f.UserCreateForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print(request.POST.get('username'))
            User.objects.create_user(
                username=data.get('username'),
                password=data.get('password'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                email=data.get('email')
            )
            return redirect('/')
        else:
            return render(request, 'register.html', {'form': form})


class LogoutView(View):
    def get(self, request):
        if request.user:
            logout(request)
        return redirect('/')

