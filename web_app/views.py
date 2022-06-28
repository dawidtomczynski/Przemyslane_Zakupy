from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User, Group
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
        plans_list = m.Plan.objects.all().order_by('date_created')
        paginator = Paginator(plans_list, 10)
        page = request.GET.get('page')
        plans = paginator.get_page(page)
        return render(request, 'plans.html', {'plans': plans})


class MealsView(View):
    def get(self, request):
        meals_list = m.Meal.objects.all().order_by('date_created')
        paginator = Paginator(meals_list, 10)
        page = request.GET.get('page')
        meals = paginator.get_page(page)
        return render(request, 'meals.html', {'meals': meals})


class ProductsView(View):
    def get(self, request):
        products_list = m.Product.objects.all().order_by('type__products')
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


class LogoutView(View):
    def get(self, request):
        if request.user:
            logout(request)
        return redirect('/')


class UserCreateView(View):
    def get(self, request):
        form = f.UserCreateForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = f.UserCreateForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = request.POST.get('username')
            User.objects.create_user(
                username=username,
                password=data.get('password'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                email=data.get('email')
            )
            user = User.objects.get(username=username)
            group = Group.objects.get(name='Client')
            user.groups.add(group)
            return redirect('/login/')
        else:
            return render(request, 'register.html', {'form': form})


class UserUpdateView(PermissionRequiredMixin, View):
    permission_required = 'auth.change_user'

    def get(self, request):
        user = request.user
        form = f.UserUpdateForm(initial={'username': user.username,
                                         'first_name': user.first_name,
                                         'last_name': user.last_name,
                                         'email': user.email})
        return render(request, 'user_update.html', {'form': form, 'user': user})

    def post(self, request):
        user = request.user
        form = f.UserUpdateForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user.username = request.POST.get('username')
            user.first_name = data.get('first_name')
            user.last_name = data.get('last_name')
            user.email = data.get('email')
            user.save()
            msg = 'Pomyślnie zapisano zmiany.'
            return render(request, 'user_update.html', {'form': form, 'msg': msg})
        return render(request, 'user_update.html', {'form': form})


class UserUpdatePasswordView(PermissionRequiredMixin, View):
    permission_required = 'auth.change_user'

    def get(self, request):
        form = f.UserUpdatePasswordForm()
        return render(request, 'user_update_password.html', {'form': form})

    def post(self, request):
        user = request.user
        form = f.UserUpdatePasswordForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user.set_password(data.get('new_password'))
            user.save()
            msg = 'Hasło pomyślnie zmienione.'
            return render(request, 'user_update_password.html', {'form': form, 'msg': msg})
        else:
            return render(request, 'user_update_password.html', {'form': form})


class UserDeleteView(View):
    def get(self, request):
        user = request.user
        user.delete()
        return redirect('/')
