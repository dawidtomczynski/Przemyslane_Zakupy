import random
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.views import View
from web_app import models as m
from web_app import forms as f


class BaseView(View):
    def get(self, request):
        random_meals = list(m.Meal.objects.all())
        random.shuffle(random_meals)
        return render(request, 'base.html', {'random_meals': random_meals})


class PlanListView(View):
    def get(self, request):
        plans_list = m.Plan.objects.all().order_by('date_created')
        paginator = Paginator(plans_list, 10)
        page = request.GET.get('page')
        plans = paginator.get_page(page)
        random_plans = list(m.Plan.objects.all())
        random.shuffle(random_plans)
        return render(request, 'plans.html', {'plans': plans, 'random_plans': random_plans})


class PlanDetailsView(View):
    def get(self, request, plan_id):
        plan = get_object_or_404(m.Plan, id=plan_id)
        meals = m.Meal.objects.filter(plan=plan_id)
        return render(request, 'plan_details.html', {'plan': plan, 'meals': meals})


class PlanAddView(PermissionRequiredMixin, View):
    permission_required = 'web_app.add_plan'

    def get(self, request):
        form = f.PlanAddForm()
        return render(request, 'add_plan.html', {'form': form})

    def post(self, request):
        form = f.PlanAddForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            m.Plan.objects.create(name=data.get('name'),
                                  user=request.user,
                                  type=data.get('type'),
                                  persons=data.get('persons'))
            last_plan = m.Plan.objects.last()
            last_plan.meal.set(data.get('meal'))
            return redirect(f"/plans/{last_plan.id}")
        return render(request, 'add_plan.html', {'form': form})


class PlanModifyView(PermissionRequiredMixin, View):
    permission_required = 'web_app.change_plan'

    def get(self, request, plan_id):
        plan = get_object_or_404(m.Plan, id=plan_id)
        user = request.user
        if user == plan.user:
            meals_ids = list(plan.meal.values_list('id', flat=True))
            form = f.PlanAddForm(initial={'name': plan.name, 'type': plan.type, 'persons': plan.persons, 'meal': meals_ids})
            return render(request, 'add_plan.html', {'form': form})
        else:
            msg = 'Nie możesz edytować czyjegoś planu.'
            return render(request, 'add_plan.html', {'msg': msg})

    def post(self, request, plan_id):
        plan = get_object_or_404(m.Plan, id=plan_id)
        user = request.user
        if plan.user == user:
            form = f.PlanAddForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                plan.name=data.get('name')
                plan.type=data.get('type')
                plan.persons=data.get('persons')
                plan.meal.set(data.get('meal'))
                return redirect(f"/plans/{plan_id}")
            return render(request, 'add_plan.html', {'form': form})
        else:
            msg = 'Nie możesz edytować czyjegoś planu.'
            return render(request, 'add_plan.html', {'msg': msg})


class PlanDeleteView(PermissionRequiredMixin, View):
    permission_required = 'web_app.delete_plan'

    def get(self, request, plan_id):
        plan = get_object_or_404(m.Plan, id=plan_id)
        user = request.user
        if user == plan.user:
            return render(request, 'delete_plan.html', {'plan': plan})
        else:
            msg = 'Nie możesz usunąć czyjegoś planu.'
        return render(request, 'delete_plan.html', {'msg': msg})

    def post(self, request, plan_id):
        plan = get_object_or_404(m.Plan, id=plan_id)
        user = request.user
        if user == plan.user:
            if request.POST.get('answer') == 'Tak':
                plan.delete()
                return redirect('/plans/')
            else:
                return redirect(f"/plans/{plan_id}")
        else:
            msg = 'Nie możesz usunąć czyjegoś planu.'
        return render(request, 'delete_plan.html', {'msg': msg})


class MealListView(View):
    def get(self, request):
        meals_list = m.Meal.objects.all().order_by('date_created')
        paginator = Paginator(meals_list, 10)
        page = request.GET.get('page')
        meals = paginator.get_page(page)
        random_meals = list(m.Meal.objects.all())
        random.shuffle(random_meals)
        return render(request, 'meals.html', {'meals': meals, 'random_meals': random_meals})


class ProductListView(View):
    def get(self, request):
        products_list = m.Product.objects.all().order_by('name')
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


class UserDeleteView(PermissionRequiredMixin, View):
    permission_required = 'auth.delete_user'

    def get(self, request):
        user = request.user
        user.delete()
        return redirect('/')
