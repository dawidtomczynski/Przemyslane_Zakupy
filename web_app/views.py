import random
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.views import View
from web_app import models as m
from web_app import forms as f


class LoginView(View):
    def get(self, request):
        form = f.LoginForm()
        return render(request, 'user_login.html', {'form': form})

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
                return render(request, 'user_login.html', {'form': form, 'msg': msg})
        else:
            return render(request, 'user_login.html', {'form': form})


class LogoutView(View):
    def get(self, request):
        if request.user:
            logout(request)
        return redirect('/')


class UserCreateView(View):

    def get(self, request):
        form = f.UserCreateForm()
        return render(request, 'user_register.html', {'form': form})

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
            return render(request, 'user_register.html', {'form': form})


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


class BaseView(View):
    def get(self, request):
        random_meals = list(m.Meal.objects.all())
        random.shuffle(random_meals)
        return render(request, 'base.html', {'random_meals': random_meals})


class PlanListView(View):
    def get(self, request):
        if request.GET.get('search'):
            plans_list = m.Plan.objects.filter(name__icontains=request.GET.get('search')).order_by('date_created')
        else:
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
        if request.user.is_authenticated:
            form = f.PlanAddForm()
            return render(request, 'plan_add.html', {'form': form})
        else:
            msg = 'Tylko zalogowany użytkownik może dodawać plany.'
            return render(request, 'plan_add.html', {'msg': msg})

    def post(self, request):
        if request.user.is_authenticated:
            form = f.PlanAddForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                m.Plan.objects.create(name=data.get('name'),
                                      user=request.user,
                                      type=data.get('type'),
                                      persons=data.get('persons'))
                last_plan = m.Plan.objects.last()
                return redirect(f"/plans/{last_plan.id}")
            return render(request, 'plan_add.html', {'form': form})
        else:
            msg = 'Tylko zalogowany użytkownik może dodawać plany.'
            return render(request, 'plan_add.html', {'msg': msg})


class PlanModifyView(PermissionRequiredMixin, View):
    permission_required = 'web_app.change_plan'

    def get(self, request, plan_id):
        plan = get_object_or_404(m.Plan, id=plan_id)
        user = request.user
        if user == plan.user:
            meals_ids = list(plan.meal.values_list('id', flat=True))
            form = f.PlanAddForm(initial={'name': plan.name, 'type': plan.type,
                                          'persons': plan.persons})
            return render(request, 'plan_add.html', {'form': form})
        else:
            msg = 'Nie możesz edytować czyjegoś planu.'
            return render(request, 'plan_add.html', {'msg': msg})

    def post(self, request, plan_id):
        plan = get_object_or_404(m.Plan, id=plan_id)
        user = request.user
        if plan.user == user:
            form = f.PlanAddForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                plan.name = data.get('name')
                plan.type = data.get('type')
                plan.persons = data.get('persons')
                plan.save()
                return redirect(f"/plans/{plan_id}")
            return render(request, 'plan_add.html', {'form': form})
        else:
            msg = 'Nie możesz edytować czyjegoś planu.'
            return render(request, 'plan_add.html', {'msg': msg})


class PlanDeleteView(PermissionRequiredMixin, View):
    permission_required = 'web_app.delete_plan'

    def get(self, request, plan_id):
        plan = get_object_or_404(m.Plan, id=plan_id)
        user = request.user
        if user == plan.user:
            return render(request, 'plan_delete.html', {'plan': plan})
        else:
            msg = 'Nie możesz usunąć czyjegoś planu.'
        return render(request, 'plan_delete.html', {'msg': msg})

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
        return render(request, 'plan_delete.html', {'msg': msg})


class PlanMealAddView(PermissionRequiredMixin, View):
    permission_required = 'web_app.add_planmeal'

    def get(self, request, plan_id):
        user = request.user
        plan = get_object_or_404(m.Plan, id=plan_id)
        if plan.user == user:
            chosen_meals = m.Meal.objects.filter(plan=plan_id)
            meals = m.Meal.objects.exclude(plan=plan_id)
            return render(request, 'plan_meal_add.html', {'plan': plan, 'meals': meals, 'chosen_meals': chosen_meals})
        else:
            msg = 'Nie możesz edytować czyjegoś planu.'
            return render(request, 'plan_meal_add.html', {'msg': msg})

    def post(self, request, plan_id):
        user = request.user
        plan = get_object_or_404(m.Plan, id=plan_id)
        if plan.user == user:
            meals = request.POST.getlist('meal')
            plan.meal.set(meals)
            plan.save()
            return redirect(f"/plans/{plan_id}")
        else:
            msg = 'Nie możesz edytować czyjegoś planu.'
            return render(request, 'plan_meal_add.html', {'msg': msg})


class PlanMealRandomAdd(PermissionRequiredMixin, View):
    permission_required = 'web_app.add_planmeal'

    def get(self, request, plan_id):
        user = request.user
        plan = get_object_or_404(m.Plan, id=plan_id)
        if plan.user == user:
            meals = list(m.Meal.objects.all().exclude(plan=plan))
            random.shuffle(meals)
            try:
                m.PlanMeal.objects.create(plan_id=plan_id, meal_id=meals[0].id)
            except IndexError:
                pass
            return redirect(f"/plans/add-meal/{plan_id}")
        else:
            msg = 'Nie możesz edytować czyjegoś planu.'
            return render(request, 'plan_meal_add.html', {'msg': msg})




class MealListView(View):
    def get(self, request):
        if request.GET.get('search'):
            meals_list = m.Meal.objects.filter(name__icontains=request.GET.get('search')).order_by('date_created')
        else:
            meals_list = m.Meal.objects.all().order_by('date_created')
        paginator = Paginator(meals_list, 10)
        page = request.GET.get('page')
        meals = paginator.get_page(page)
        random_meals = list(m.Meal.objects.all())
        random.shuffle(random_meals)
        return render(request, 'meals.html', {'meals': meals, 'random_meals': random_meals})


class MealDetailsView(View):
    def get(self, request, meal_id):
        meal = get_object_or_404(m.Meal, id=meal_id)
        products = m.Product.objects.filter(meal=meal_id)
        return render(request, 'meal_details.html', {'meal': meal, 'products': products})


class MealAddView(PermissionRequiredMixin, View):
    permission_required = 'web_app.add_meal'

    def get(self, request):
        if request.user.is_authenticated:
            form = f.MealAddForm()
            return render(request, 'meal_add.html', {'form': form})
        else:
            msg = 'Tylko zalogowany użytkownik może dodawać dania.'
            return render(request, 'meal_add.html', {'msg': msg})

    def post(self, request):
        if request.user.is_authenticated:
            form = f.MealAddForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                m.Meal.objects.create(name=data.get('name'), user=request.user,
                                      recipe=data.get('recipe'), type=data.get('type'))
                last_meal = m.Meal.objects.last()
                return redirect(f"/meals/{last_meal.id}")
            return render(request, 'meal_add.html', {'form': form})
        else:
            msg = 'Tylko zalogowany użytkownik może dodawać dania.'
            return render(request, 'meal_add.html', {'msg': msg})


class MealModifyView(PermissionRequiredMixin, View):
    permission_required = 'web_app.change_meal'

    def get(self, request, meal_id):
        meal = get_object_or_404(m.Meal, id=meal_id)
        user = request.user
        if user == meal.user:
            products_ids = list(meal.product.values_list('id', flat=True))
            form = f.MealAddForm(initial={'name': meal.name, 'type': meal.type,
                                          'recipe': meal.recipe, 'product': products_ids})
            return render(request, 'meal_add.html', {'form': form})
        else:
            msg = 'Nie możesz edytować czyjegoś dania.'
            return render(request, 'meal_add.html', {'msg': msg})

    def post(self, request, meal_id):
        meal = get_object_or_404(m.Meal, id=meal_id)
        user = request.user
        if meal.user == user:
            form = f.MealAddForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                meal.name = data.get('name')
                meal.type = data.get('type')
                meal.recipe = data.get('recipe')
                meal.save()
                return redirect(f"/meals/{meal_id}")
            return render(request, 'meal_add.html', {'form': form})
        else:
            msg = 'Nie możesz edytować czyjegoś dania.'
            return render(request, 'meal_add.html', {'msg': msg})


class MealDeleteView(PermissionRequiredMixin, View):
    permission_required = 'web_app.delete_meal'

    def get(self, request, meal_id):
        meal = get_object_or_404(m.Meal, id=meal_id)
        user = request.user
        if user == meal.user:
            return render(request, 'meal_delete.html', {'meal': meal})
        else:
            msg = 'Nie możesz usunąć czyjegoś dania.'
        return render(request, 'meal_delete.html', {'msg': msg})

    def post(self, request, meal_id):
        meal = get_object_or_404(m.Meal, id=meal_id)
        user = request.user
        if user == meal.user:
            if request.POST.get('answer') == 'Tak':
                meal.delete()
                return redirect('/meals/')
            else:
                return redirect(f"/meals/{meal_id}")
        else:
            msg = 'Nie możesz usunąć czyjegoś dania.'
        return render(request, 'meal_delete.html', {'msg': msg})


class MealPlanAddView(PermissionRequiredMixin, View):
    permission_required = 'web_app.add_planmeal'

    def get(self, request, meal_id):
        user = request.user
        meal = get_object_or_404(m.Meal, id=meal_id)
        plans = m.Plan.objects.filter(user=user).exclude(planmeal__meal=meal_id)
        chosen_plans = m.Plan.objects.filter(user=user, planmeal__meal=meal_id)
        return render(request, 'meal_plan_add.html', {'meal': meal, 'plans': plans, 'chosen_plans': chosen_plans})

    def post(self, request, meal_id):
        meal = get_object_or_404(m.Meal, id=meal_id)
        plans = request.POST.getlist('plan')
        for plan in plans:
            m.PlanMeal.objects.create(plan_id=plan, meal_id=meal.id)
        msg = 'Dodano danie do wybranego planu / ów.'
        products = m.Product.objects.filter(meal=meal_id)
        return render(request, 'meal_details.html', {'meal': meal, 'products': products, 'msg': msg})


class MealProductAddView(PermissionRequiredMixin, View):
    permission_required = 'web_app.add_mealproduct'

    def get(self, request, meal_id):
        user = request.user
        meal = get_object_or_404(m.Meal, id=meal_id)
        if meal.user == user:
            chosen_products = m.Product.objects.filter(meal=meal_id)
            products = m.Product.objects.exclude(meal=meal_id)
            return render(request, 'meal_product_add.html', {'meal': meal, 'products': products,
                                                             'chosen_products': chosen_products})
        else:
            msg = 'Nie możesz edytować czyjegoś dania.'
            return render(request, 'meal_product_add.html', {'msg': msg})

    def post(self, request, meal_id):
        user = request.user
        meal = get_object_or_404(m.Meal, id=meal_id)
        if meal.user == user:
            products = request.POST.getlist('product')
            meal.product.set(products)
            meal.save()
            return redirect(f"/meals/{meal_id}")
        else:
            msg = 'Nie możesz edytować czyjegoś dania.'
            return render(request, 'meal_product_add.html', {'msg': msg})


class MealProductGramsSet(View):
    def get(self, request, meal_id, product_id):
        meal_product = get_object_or_404(m.MealProduct, meal_id=meal_id, product_id=product_id)
        return render(request, 'meal_product_grams_set.html', {'meal_product': meal_product})

    def post(self, request, meal_id, product_id):
        meal_product = get_object_or_404(m.MealProduct, meal_id=meal_id, product_id=product_id)
        meal_product.grams = request.POST.get('grams')
        meal_product.save()
        return redirect(f"/meals/{meal_id}")


class ProductListView(View):
    def get(self, request):
        products_list = m.Product.objects.all().order_by('type')
        paginator = Paginator(products_list, 10)
        page = request.GET.get('page')
        products = paginator.get_page(page)
        return render(request, 'products.html', {'products': products})


class ProductDetailsView(View):
    def get(self, request, product_id):
        product = get_object_or_404(m.Product, id=product_id)
        return render(request, 'product_details.html', {'product': product})


class ProductAddView(PermissionRequiredMixin, View):
    permission_required = 'web_app.add_product'

    def get(self, request):
        form = f.ProductAddForm()
        return render(request, 'product_add.html', {'form': form})

    def post(self, request):
        form = f.ProductAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/products/')
        return render(request, 'product_add.html', {'form': form})


class ProductModifyView(PermissionRequiredMixin, View):
    permission_required = 'web_app.change_product'

    def get(self, request, product_id):
        product = m.Product.objects.get(id=product_id)
        form = f.ProductAddForm(instance=product)
        return render(request, 'product_add.html', {'form': form})

    def post(self, request, product_id):
        product = m.Product.objects.get(id=product_id)
        form = f.ProductAddForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect(f"/products/{product_id}")
        return render(request, 'product_add.html', {'form': form})


class ProductDeleteView(PermissionRequiredMixin, View):
    permission_required = 'web_app.delete_product'

    def get(self, request, product_id):
        product = m.Product.objects.get(id=product_id)
        return render(request, 'product_delete.html', {'product': product})

    def post(self, request, product_id):
        product = m.Product.objects.get(id=product_id)
        if request.POST.get('answer') == 'Tak':
            product.delete()
            return redirect('/products/')
        return redirect(f"/products/{product_id}")


class ProductTypeListView(PermissionRequiredMixin, View):
    permission_required = 'web_app.view_producttype'

    def get(self, request):
        product_types = m.ProductType.objects.all()
        return render(request, 'product_types.html', {'product_types': product_types})


class ProductTypeAddView(PermissionRequiredMixin, View):
    permission_required = 'web_app.add_producttype'

    def get(self, request):
        form = f.ProductTypeAddForm()
        return render(request, 'product_type_add.html', {'form': form})

    def post(self, request):
        form = f.ProductTypeAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(f"/products/types/")
        return render(request, 'product_type_add.html', {'form': form})


class ProductTypeModifyView(PermissionRequiredMixin, View):
    permission_required = 'web_app.change_producttype'

    def get(self, request, product_type_id):
        product_type = m.ProductType.objects.get(id=product_type_id)
        form = f.ProductTypeAddForm(instance=product_type)
        return render(request, 'product_type_add.html', {'form': form})

    def post(self, request, product_type_id):
        product_type = m.ProductType.objects.get(id=product_type_id)
        form = f.ProductTypeAddForm(request.POST, instance=product_type)
        if form.is_valid():
            form.save()
            return redirect('/products/types/')
        return render(request, 'product_type_add.html', {'form': form})


class ProductTypeDeleteView(PermissionRequiredMixin, View):
    permission_required = 'web_app.delete_producttype'

    def get(self, request, product_type_id):
        product_type = m.ProductType.objects.get(id=product_type_id)
        return render(request, 'product_type_delete.html', {'product_type': product_type})

    def post(self, request, product_type_id):
        product_type = m.ProductType.objects.get(id=product_type_id)
        if request.POST.get('answer') == 'Tak':
            product_type.delete()
        return redirect('/products/types/')


class UserPlanListView(View):
    def get(self, request):
        user = request.user
        user_plans = m.Plan.objects.filter(user=user)
        return render(request, 'user_plans.html', {'user_plans': user_plans})


class UserFavouritePlanListView(View):
    def get(self, request):
        user = request.user
        favourite_plans = m.Plan.objects.filter(favouriteplan__user=user)
        return render(request, 'user_favourite_plans.html', {'favourite_plans': favourite_plans})


class UserFavouritePlanAddView(PermissionRequiredMixin, View):
    permission_required = 'web_app.add_favouriteplan'

    def get(self, request, plan_id):
        user = request.user
        try:
            favourite_plans = m.FavouritePlan.objects.get(user=user)
        except ObjectDoesNotExist:
            m.FavouritePlan.objects.create(user=user)
            favourite_plans = m.FavouritePlan.objects.get(user=user)
        favourite_plans.plan.add(plan_id)
        return redirect(f"/plans/{plan_id}/")


class UserFavouritePlanDeleteView(PermissionRequiredMixin, View):
    permission_required = 'web_app.delete_favouriteplan'

    def get(self, request, plan_id):
        user = request.user
        favourite_plans = m.FavouritePlan.objects.get(user=user)
        favourite_plans.plan.remove(plan_id)
        return redirect('/profile/favourite-plans/')


class UserMealList(View):
    def get(self, request):
        user = request.user
        user_meals = m.Meal.objects.filter(user=user)
        return render(request, 'user_meals.html', {'user_meals': user_meals})


class UserFavouriteMealListView(View):
    def get(self, request):
        user = request.user
        favourite_meals = m.Meal.objects.filter(favouritemeal__user=user)
        print(favourite_meals)
        return render(request, 'user_favourite_meals.html', {'favourite_meals': favourite_meals})


class UserFavouriteMealAddView(PermissionRequiredMixin, View):
    permission_required = 'web_app.add_favouritemeal'

    def get(self, request, meal_id):
        user = request.user
        try:
            favourite_meals = m.FavouriteMeal.objects.get(user=user)
        except ObjectDoesNotExist:
            m.FavouriteMeal.objects.create(user=user)
            favourite_meals = m.FavouriteMeal.objects.get(user=user)
        favourite_meals.meal.add(meal_id)
        return redirect(f"/meals/{meal_id}")


class UserFavouriteMealDeleteView(PermissionRequiredMixin, View):
    permission_required = 'web_app.delete_favouritemeal'

    def get(self, request, meal_id):
        user = request.user
        favourite_meals = m.FavouriteMeal.objects.get(user=user)
        favourite_meals.meal.remove(meal_id)
        return redirect('/profile/favourite-meals/')


class UserSelectedPlanView(View):
    def get(self, request):
        user = request.user
        if user:
            try:
                selected_plan = m.SelectedPlan.objects.get(user=user)
                plan = m.Plan.objects.get(id=selected_plan.active_plan_id)
                meals = m.Meal.objects.filter(plan=plan.id)
                return render(request, 'user_selected_plan.html', {'plan': plan, 'meals': meals})
            except ObjectDoesNotExist:
                msg = 'Nie masz wybranego aktualnego planu.'
                return render(request, 'user_selected_plan.html', {'msg': msg})

        else:
            msg = 'Najpierw musisz się zalogować.'
            return render(request, 'user_selected_plan.html', {'msg': msg})


class UserSelectedPlanAddView(PermissionRequiredMixin, View):
    permission_required = 'web_app.add_selectedplan'

    def get(self, request, plan_id):
        if request.user.is_authenticated:
            plan = m.Plan.objects.get(id=plan_id)
            return render(request, 'user_selected_plan_add.html', {'plan': plan})
        else:
            msg = 'Najpierw musisz się zalogować.'
            return render(request, 'user_selected_plan_add.html', {'msg': msg})

    def post(self, request, plan_id):
        user = request.user
        if user.is_authenticated:
            try:
                selected_plan = m.SelectedPlan.objects.get(user=user)
                selected_plan.active_plan_id = plan_id
                selected_plan.save()
            except ObjectDoesNotExist:
                m.SelectedPlan.objects.create(user=user, active_plan_id=plan_id)
            return redirect('/profile/active-plan/')
        else:
            msg = 'Najpierw musisz się zalogować.'
            return render(request, 'user_selected_plan_add.html', {'msg': msg})


def products_sort(product):
    return product.type.name


class PlanProductListView(View):
    def get(self, request, plan_id):
        plan = m.Plan.objects.get(id=plan_id)
        meals = m.Meal.objects.filter(plan=plan)
        products_list = []
        cost = 0
        for meal in meals:
            products = m.Product.objects.filter(meal=meal)
            for product in products:
                products_list.append(product)
                cost += product.price
        products_list.sort(key=products_sort, reverse=True)
        return render(request, 'plan_product_list.html', {'plan': plan, 'meals': meals,
                                                          'products': products_list, 'cost': cost})
