import random
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from web_app import models as m
from web_app import forms as f


class LoginView(View):
    """
    Logs in registered user.
    """
    def get(self, request):
        """
        Shows login form on screen.
        """
        form = f.LoginForm()
        return render(request, 'user_login.html', {'form': form})

    def post(self, request):
        """
        Logs user in if given the right data and redirects to main site.
        """
        form = f.LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = data.get('username')
            password = data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('base_view')
            else:
                msg = 'Podano nieprawidłowe dane logowania.'
                return render(request, 'user_login.html', {'form': form, 'msg': msg})
        else:
            return render(request, 'user_login.html', {'form': form})


class LogoutView(View):
    """
    Logs out already logged in user.
    """
    def get(self, request):
        """
        Logs user out and redirects to main site
        """
        if request.user:
            logout(request)
        return redirect('base_view')


class UserCreateView(View):
    """
    Creates new user.
    """
    def get(self, request):
        """
        Shows new user create form on screen
        """
        form = f.UserCreateForm()
        return render(request, 'user_register.html', {'form': form})

    def post(self, request):
        """
        Creats new user with given data and redirects to login site.
        """
        form = f.UserCreateForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = request.POST.get('username')
            user = User.objects.create_user(
                username=username,
                password=data.get('password'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                email=data.get('email')
            )
            group = Group.objects.get(name='Client')
            user.groups.add(group)
            return redirect('user_login')
        else:
            return render(request, 'user_register.html', {'form': form})


class UserUpdateView(PermissionRequiredMixin, View):
    """
    Updates data of already existing and logged in user, no password update option.
    """
    permission_required = 'auth.change_user'

    def get(self, request):
        """
        Shows user update form filled with user's data.
        """
        user = request.user
        form = f.UserUpdateForm(initial={'username': user.username,
                                         'first_name': user.first_name,
                                         'last_name': user.last_name,
                                         'email': user.email})
        return render(request, 'user_update.html', {'form': form, 'user': user})

    def post(self, request):
        """
        Updates user's data with given new data.
        """
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
    """
    Updates password of already existing and logged in user.
    """
    permission_required = 'auth.change_user'

    def get(self, request):
        """
        Shows password update form on screen.
        """
        form = f.UserUpdatePasswordForm()
        return render(request, 'user_update_password.html', {'form': form})

    def post(self, request):
        """
        Updates user's password with given new password.
        """
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
    """
    Deletes already existing and logged in user.
    """
    permission_required = 'auth.delete_user'

    def get(self, request):
        """
        Deletes the user and redirects to main site.
        """
        user = request.user
        user.delete()
        return redirect('base_view')


class BaseView(View):
    """
    Shows base html template with 3 random meals on main site.
    """
    def get(self, request):
        random_meals = list(m.Meal.objects.all())
        random.shuffle(random_meals)
        return render(request, 'base.html', {'random_meals': random_meals})


class PlanListView(View):
    """
    Shows all plans on screen with search option.
    """
    def get(self, request):
        """
        Shows all plans as list with cost of each plan and 3 random plans on top.
        """
        plans = m.Plan.objects.all().order_by('date_created')
        random_plans = list(m.Plan.objects.all())
        random.shuffle(random_plans)
        return render(request, 'plans.html', {'plans': plans, 'random_plans': random_plans})


class PlanDetailsView(View):
    """
    Shows specific plan details.
    """
    def get(self, request, plan_id):
        """
        Shows specific plan details, such as cost, for how many persons, meals in plan.
        """
        plan = get_object_or_404(m.Plan, id=plan_id)
        meals = m.Meal.objects.filter(plan=plan_id)
        return render(request, 'plan_details.html', {'plan': plan, 'meals': meals})


class PlanAddView(PermissionRequiredMixin, View):
    """
    Ads new plan by logged in user.
    """
    permission_required = 'web_app.add_plan'

    def get(self, request):
        """
        Shows new plan add form on screen, only for logged in user.
        """
        if request.user.is_authenticated:
            form = f.PlanAddForm()
            return render(request, 'plan_add.html', {'form': form})
        else:
            msg = 'Tylko zalogowany użytkownik może dodawać plany.'
            return render(request, 'plan_add.html', {'msg': msg})

    def post(self, request):
        """
        Saves new plan with given data, redirects to this plan details site.
        """
        if request.user.is_authenticated:
            form = f.PlanAddForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                m.Plan.objects.create(name=data.get('name'),
                                      user=request.user,
                                      type=data.get('type'),
                                      persons=data.get('persons'))
                last_plan = m.Plan.objects.last()
                return redirect('plan_details', plan_id=last_plan.id)
            return render(request, 'plan_add.html', {'form': form})
        else:
            msg = 'Tylko zalogowany użytkownik może dodawać plany.'
            return render(request, 'plan_add.html', {'msg': msg})


class PlanModifyView(PermissionRequiredMixin, View):
    """
    Modifies specified plan details, only for logged in plan's creator.
    """
    permission_required = 'web_app.change_plan'

    def get(self, request, plan_id):
        """
        Shows modify plan form filled with plan details.
        """
        plan = get_object_or_404(m.Plan, id=plan_id)
        user = request.user
        if user == plan.user:
            form = f.PlanAddForm(initial={'name': plan.name, 'type': plan.type,
                                          'persons': plan.persons})
            return render(request, 'plan_add.html', {'form': form})
        else:
            msg = 'Nie możesz edytować czyjegoś planu.'
            return render(request, 'plan_add.html', {'msg': msg})

    def post(self, request, plan_id):
        """
        Modifies plan details with given data and redirects to plan details site.
        """
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
                return redirect('plan_details', plan_id=plan_id)
            return render(request, 'plan_add.html', {'form': form})
        else:
            msg = 'Nie możesz edytować czyjegoś planu.'
            return render(request, 'plan_add.html', {'msg': msg})


class PlanDeleteView(PermissionRequiredMixin, View):
    """
    Deletes specific plan, only for logged in plan's creator.
    """
    permission_required = 'web_app.delete_plan'

    def get(self, request, plan_id):
        """
        Shows warning if user really wants to delete the plan.
        """
        plan = get_object_or_404(m.Plan, id=plan_id)
        user = request.user
        if user == plan.user:
            return render(request, 'plan_delete.html', {'plan': plan})
        else:
            msg = 'Nie możesz usunąć czyjegoś planu.'
        return render(request, 'plan_delete.html', {'msg': msg})

    def post(self, request, plan_id):
        """
        If answer is yes, deletes the plan and redirects to all plans list site.
        Otherwise, redirects to plan's details site.
        """
        plan = get_object_or_404(m.Plan, id=plan_id)
        user = request.user
        if user == plan.user:
            if request.POST.get('answer') == 'Tak':
                plan.delete()
                return redirect('plans')
            else:
                return redirect('plan_details', plan_id=plan_id)
        else:
            msg = 'Nie możesz usunąć czyjegoś planu.'
        return render(request, 'plan_delete.html', {'msg': msg})


class PlanMealAddView(PermissionRequiredMixin, View):
    """
    Ads meals to specific plan, with meal search option, only for logged in plan owner.
    """
    permission_required = 'web_app.add_planmeal'

    def get(self, request, plan_id):
        """
        Shows add meals to specific plan form on screen.
        """
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
        """
        Ads/removes chosen meal/meals to/from the plan and redirects to plan details site.
        """
        user = request.user
        plan = get_object_or_404(m.Plan, id=plan_id)
        if plan.user == user:
            meals = request.POST.getlist('meal')
            plan.meal.set(meals)
            plan.save()
            return redirect('plan_details', plan_id=plan_id)
        else:
            msg = 'Nie możesz edytować czyjegoś planu.'
            return render(request, 'plan_meal_add.html', {'msg': msg})


class PlanMealRandomAdd(PermissionRequiredMixin, View):
    """
    Ads random meal to specific plan, only for logged in plan creator.
    """
    permission_required = 'web_app.add_planmeal'

    def get(self, request, plan_id):
        """
        Gets one random meal and ads it to the plan, can be done until there are no meals left.
        """
        user = request.user
        plan = get_object_or_404(m.Plan, id=plan_id)
        if plan.user == user:
            meals = list(m.Meal.objects.all().exclude(plan=plan))
            random.shuffle(meals)
            try:
                m.PlanMeal.objects.create(plan_id=plan_id, meal_id=meals[0].id)
            except IndexError:
                pass
            return redirect('plan_meal_add', plan_id=plan_id)
        else:
            msg = 'Nie możesz edytować czyjegoś planu.'
            return render(request, 'plan_meal_add.html', {'msg': msg})


class MealListView(View):
    """
    Shows all meals on screen with search option.
    """
    def get(self, request):
        """
        Shows all meals as list with cost, kcal/100g of each meal and 3 random meals on top.
        """
        meals = m.Meal.objects.all().order_by('date_created')
        random_meals = list(m.Meal.objects.all())
        random.shuffle(random_meals)
        return render(request, 'meals.html', {'meals': meals, 'random_meals': random_meals})


class MealDetailsView(View):
    """
    Shows specific meal details
    """
    def get(self, request, meal_id):
        """
        Shows the meal details, such as cost, kcal/100g, weight, products in meal.
        """
        meal = get_object_or_404(m.Meal, id=meal_id)
        products = m.Product.objects.filter(meal=meal_id)
        return render(request, 'meal_details.html', {'meal': meal, 'products': products})


class MealAddView(PermissionRequiredMixin, View):
    """
    Ads new meal by logged in user
    """
    permission_required = 'web_app.add_meal'

    def get(self, request):
        """
        Shows new plan meal form on screen, only for logged in user.
        """
        if request.user.is_authenticated:
            form = f.MealAddForm()
            return render(request, 'meal_add.html', {'form': form})
        else:
            msg = 'Tylko zalogowany użytkownik może dodawać dania.'
            return render(request, 'meal_add.html', {'msg': msg})

    def post(self, request):
        """
        Saves new meal with given data, redirects to this meal details site.
        """
        if request.user.is_authenticated:
            form = f.MealAddForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                m.Meal.objects.create(name=data.get('name'), user=request.user,
                                      recipe=data.get('recipe'), type=data.get('type'))
                last_meal = m.Meal.objects.last()
                return redirect('meal_details', meal_id=last_meal.id)
            return render(request, 'meal_add.html', {'form': form})
        else:
            msg = 'Tylko zalogowany użytkownik może dodawać dania.'
            return render(request, 'meal_add.html', {'msg': msg})


class MealModifyView(PermissionRequiredMixin, View):
    """
    Modifies specified meal details, only for logged in meal's creator.
    """
    permission_required = 'web_app.change_meal'

    def get(self, request, meal_id):
        """
        Shows modify meal form filled with meal details.
        """
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
        """
        Modifies meal details with given data and redirects to meal details site.
        """
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
                return redirect('meal_details', meal_id=meal_id)
            return render(request, 'meal_add.html', {'form': form})
        else:
            msg = 'Nie możesz edytować czyjegoś dania.'
            return render(request, 'meal_add.html', {'msg': msg})


class MealDeleteView(PermissionRequiredMixin, View):
    """
    Deletes specific meal, only for logged in meal's creator.
    """
    permission_required = 'web_app.delete_meal'

    def get(self, request, meal_id):
        """
        Shows warning if user really wants to delete the meal.
        """
        meal = get_object_or_404(m.Meal, id=meal_id)
        user = request.user
        if user == meal.user:
            return render(request, 'meal_delete.html', {'meal': meal})
        else:
            msg = 'Nie możesz usunąć czyjegoś dania.'
        return render(request, 'meal_delete.html', {'msg': msg})

    def post(self, request, meal_id):
        """
        If answer is yes, deletes the meal and redirects to all meals list site.
        Otherwise, redirects to meal's details site.
        """
        meal = get_object_or_404(m.Meal, id=meal_id)
        user = request.user
        if user == meal.user:
            if request.POST.get('answer') == 'Tak':
                meal.delete()
                return redirect('meals')
            else:
                return redirect('meal_details', meal_id=meal_id)
        else:
            msg = 'Nie możesz usunąć czyjegoś dania.'
        return render(request, 'meal_delete.html', {'msg': msg})


class MealPlanAddView(PermissionRequiredMixin, View):
    """
    Ads specific meal to plan/plans created by user, with plan search option, only for logged user.
    """
    permission_required = 'web_app.add_planmeal'

    def get(self, request, meal_id):
        """
        Shows add meal to plans form on screen.
        """
        user = request.user
        meal = get_object_or_404(m.Meal, id=meal_id)
        plans = m.Plan.objects.filter(user=user).exclude(planmeal__meal=meal_id)
        chosen_plans = m.Plan.objects.filter(user=user, planmeal__meal=meal_id)
        return render(request, 'meal_plan_add.html', {'meal': meal, 'plans': plans, 'chosen_plans': chosen_plans})

    def post(self, request, meal_id):
        """
        Ads/removes meal to/from chosen plan/plans and redirects to meal details site.
        """
        meal = get_object_or_404(m.Meal, id=meal_id)
        plans = request.POST.getlist('plan')
        for plan in plans:
            m.PlanMeal.objects.create(plan_id=plan, meal_id=meal.id)
        msg = 'Dodano danie do wybranego planu / ów.'
        products = m.Product.objects.filter(meal=meal_id)
        return render(request, 'meal_details.html', {'meal': meal, 'products': products, 'msg': msg})


class MealProductAddView(PermissionRequiredMixin, View):
    """
    Ads products to specific meal, with product search option, only for logged in meal owner.
    """
    permission_required = 'web_app.add_mealproduct'

    def get(self, request, meal_id):
        """
        Shows add products to meal form on screen.
        """
        user = request.user
        meal = get_object_or_404(m.Meal, id=meal_id)
        if meal.user == user:
            chosen_products = m.Product.objects.filter(meal=meal_id)
            products = m.Product.objects.exclude(meal=meal_id)
            product_types = m.ProductType.objects.all()
            return render(request, 'meal_product_add.html', {'meal': meal, 'products': products,
                                                             'chosen_products': chosen_products,
                                                             'product_types': product_types})
        else:
            msg = 'Nie możesz edytować czyjegoś dania.'
            return render(request, 'meal_product_add.html', {'msg': msg})

    def post(self, request, meal_id):
        """
        Ads/removes chosen product/products to/from the meal and redirects to meal details site.
        """
        user = request.user
        meal = get_object_or_404(m.Meal, id=meal_id)
        if meal.user == user:
            products = request.POST.getlist('product')
            meal.product.set(products)
            meal.save()
            return redirect('meal_details', meal_id=meal_id)
        else:
            msg = 'Nie możesz edytować czyjegoś dania.'
            return render(request, 'meal_product_add.html', {'msg': msg})


class MealProductGramsSet(View):
    """
    Sets grammage of specific product in specific meal, only for logged in meal creator.
    """
    def get(self, request, meal_id, product_id):
        """
        Shows set product grammage form on screen.
        """
        meal_product = get_object_or_404(m.MealProduct, meal_id=meal_id, product_id=product_id)
        return render(request, 'meal_product_grams_set.html', {'meal_product': meal_product})

    def post(self, request, meal_id, product_id):
        """
        Sets given product grammage in meal and redirects to meal details site
        """
        meal_product = get_object_or_404(m.MealProduct, meal_id=meal_id, product_id=product_id)
        meal_product.grams = request.POST.get('grams')
        meal_product.save()
        return redirect('meal_details', meal_id=meal_id)


class ProductListView(View):
    """
    Shows all products on screen with search option.
    """
    def get(self, request):
        """
        Shows all products as list with price of each product.
        """
        products = m.Product.objects.all().order_by('type')
        product_types = m.ProductType.objects.all()
        return render(request, 'products.html', {'products': products, 'product_types': product_types})


class ProductDetailsView(View):
    """
    Shows specific product details.
    """
    def get(self, request, product_id):
        """
        Shows specific product details, such as price, kcal/100g, type.
        """
        product = get_object_or_404(m.Product, id=product_id)
        return render(request, 'product_details.html', {'product': product})


class ProductAddView(PermissionRequiredMixin, View):
    """
    Ads new product by admin.
    """
    permission_required = 'web_app.add_product'

    def get(self, request):
        """
        Shows new product add form on screen, only for admin.
        """
        form = f.ProductAddForm()
        return render(request, 'product_add.html', {'form': form})

    def post(self, request):
        """
        Saves new product with given data, redirects to products list site.
        """
        form = f.ProductAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('products')
        return render(request, 'product_add.html', {'form': form})


class ProductModifyView(PermissionRequiredMixin, View):
    """
    Modifies specified plan details, only for logged in plan's creator.
    """
    permission_required = 'web_app.change_product'

    def get(self, request, product_id):
        """
        Shows modify product form filled with product details.
        """
        product = m.Product.objects.get(id=product_id)
        form = f.ProductAddForm(instance=product)
        return render(request, 'product_add.html', {'form': form})

    def post(self, request, product_id):
        """
        Modifies product details with given data and redirects to product details site.
        """
        product = m.Product.objects.get(id=product_id)
        form = f.ProductAddForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_details', product_id=product_id)
        return render(request, 'product_add.html', {'form': form})


class ProductDeleteView(PermissionRequiredMixin, View):
    """
    Deletes specific product, only for admin.
    """
    permission_required = 'web_app.delete_product'

    def get(self, request, product_id):
        """
        Shows warning if admin really wants to delete the product.
        """
        product = m.Product.objects.get(id=product_id)
        return render(request, 'product_delete.html', {'product': product})

    def post(self, request, product_id):
        """
        If answer is yes, deletes the product and redirects to all products list site.
        Otherwise, redirects to product details site.
        """
        product = m.Product.objects.get(id=product_id)
        if request.POST.get('answer') == 'Tak':
            product.delete()
            return redirect('products')
        return redirect('product_details', product_id=product_id)


class ProductTypeListView(PermissionRequiredMixin, View):
    """
    Shows all product types on screen, only for admin.
    """
    permission_required = 'web_app.view_producttype'

    def get(self, request):
        """
        Shows all product types as list.
        """
        product_types = m.ProductType.objects.all()
        return render(request, 'product_types.html', {'product_types': product_types})


class ProductTypeAddView(PermissionRequiredMixin, View):
    """
    Ads new product type by admin.
    """
    permission_required = 'web_app.add_producttype'

    def get(self, request):
        """
        Shows new product type add form on screen, only for admin.
        """
        form = f.ProductTypeAddForm()
        return render(request, 'product_type_add.html', {'form': form})

    def post(self, request):
        """
        Saves new product type with given data, redirects to product types list site.
        """
        form = f.ProductTypeAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_types')
        return render(request, 'product_type_add.html', {'form': form})


class ProductTypeModifyView(PermissionRequiredMixin, View):
    """
    Modifies specified product type details, only for admin.
    """
    permission_required = 'web_app.change_producttype'

    def get(self, request, product_type_id):
        """
        Shows modify product type form filled with product type details.
        """
        product_type = m.ProductType.objects.get(id=product_type_id)
        form = f.ProductTypeAddForm(instance=product_type)
        return render(request, 'product_type_add.html', {'form': form})

    def post(self, request, product_type_id):
        """
        Modifies product type details with given data and redirects to product types list site.
        """
        product_type = m.ProductType.objects.get(id=product_type_id)
        form = f.ProductTypeAddForm(request.POST, instance=product_type)
        if form.is_valid():
            form.save()
            return redirect('product_types')
        return render(request, 'product_type_add.html', {'form': form})


class ProductTypeDeleteView(PermissionRequiredMixin, View):
    """
    Deletes specific product type, only for admin.
    """
    permission_required = 'web_app.delete_producttype'

    def get(self, request, product_type_id):
        """
        Shows warning if admin really wants to delete the product type.
        """
        product_type = m.ProductType.objects.get(id=product_type_id)
        return render(request, 'product_type_delete.html', {'product_type': product_type})

    def post(self, request, product_type_id):
        """
        If answer is yes, deletes the product type. Always redirects to product types list site.
        """
        product_type = m.ProductType.objects.get(id=product_type_id)
        if request.POST.get('answer') == 'Tak':
            product_type.delete()
        return redirect('product_types')


class UserPlanListView(View):
    """
    Shows plans created by user on screen, only for logged in user.
    """
    def get(self, request):
        """
        Shows plans created by user as list with cost of each plan.
        """
        user = request.user
        try:
            user_plans = m.Plan.objects.filter(user=user)
            return render(request, 'user_plans.html', {'user_plans': user_plans})
        except TypeError:
            return redirect('login')


class UserFavouritePlanListView(PermissionRequiredMixin, View):
    """
    Shows plans selected by user as favourite on screen, only for logged in user.
    """
    permission_required = 'web_app.view_favouriteplan'

    def get(self, request):
        """
        Shows plans selected by user as favourites as list with cost of each plan.
        """
        user = request.user
        favourite_plans = m.Plan.objects.filter(favouriteplan__user=user)
        return render(request, 'user_favourite_plans.html', {'favourite_plans': favourite_plans})


class UserFavouritePlanAddView(PermissionRequiredMixin, View):
    """
    Ads specific plan to favourites by logged in user.
    """
    permission_required = 'web_app.add_favouriteplan'

    def get(self, request, plan_id):
        """
        Saves plan as user's favourite, redirects to this plan details site, only for logged in user.
        """
        user = request.user
        try:
            favourite_plans = m.FavouritePlan.objects.get(user=user)
        except ObjectDoesNotExist:
            favourite_plans= m.FavouritePlan.objects.create(user=user)
        favourite_plans.plan.add(plan_id)
        return redirect('plan_details', plan_id=plan_id)


class UserFavouritePlanDeleteView(PermissionRequiredMixin, View):
    """
    Removes specific plan from favourites by logged in user.
    """
    permission_required = 'web_app.delete_favouriteplan'

    def get(self, request, plan_id):
        """
        Removes plan from user's favourite plans, redirects to user's favourite plans site,
        only for logged in user.
        """
        user = request.user
        favourite_plans = m.FavouritePlan.objects.get(user=user)
        favourite_plans.plan.remove(plan_id)
        return redirect('user_favourite_plans')


class UserMealList(View):
    """
    Shows meals created by user on screen, only for logged in user.
    """
    def get(self, request):
        """
        Shows meals created by user as list with cost of each meal.
        """
        user = request.user
        try:
            user_meals = m.Meal.objects.filter(user=user)
            return render(request, 'user_meals.html', {'user_meals': user_meals})
        except TypeError:
            return redirect('login')


class UserFavouriteMealListView(PermissionRequiredMixin, View):
    """
    Shows meals selected by user as favourite on screen, only for logged in user.
    """
    permission_required = 'web_app.view_favouritemeal'

    def get(self, request):
        """
        Shows meals selected by user as favourite as list with cost of each meal.
        """
        user = request.user
        favourite_meals = m.Meal.objects.filter(favouritemeal__user=user)
        return render(request, 'user_favourite_meals.html', {'favourite_meals': favourite_meals})


class UserFavouriteMealAddView(PermissionRequiredMixin, View):
    """
    Ads specific meal to favourite by logged in user.
    """
    permission_required = 'web_app.add_favouritemeal'

    def get(self, request, meal_id):
        """
        Saves meal as user's favourite, redirects to this meal details site, only for logged in user.
        """
        user = request.user
        try:
            favourite_meals = m.FavouriteMeal.objects.get(user=user)
        except ObjectDoesNotExist:
            m.FavouriteMeal.objects.create(user=user)
            favourite_meals = m.FavouriteMeal.objects.get(user=user)
        favourite_meals.meal.add(meal_id)
        return redirect('meal_details', meal_id=meal_id)


class UserFavouriteMealDeleteView(PermissionRequiredMixin, View):
    """
    Removes specific meal from favourites by logged in user.
    """
    permission_required = 'web_app.delete_favouritemeal'

    def get(self, request, meal_id):
        """
        Removes meal from user's favourite meals, redirects to user's favourite meals site,
        only for logged in user.
        """
        user = request.user
        favourite_meals = m.FavouriteMeal.objects.get(user=user)
        favourite_meals.meal.remove(meal_id)
        return redirect('user_favourite_meals')


class UserSelectedPlanView(PermissionRequiredMixin, View):
    """
    Shows plan selected by user as active plan on screen, only for logged in user.
    """
    permission_required = 'web_app.view_selectedplan'

    def get(self, request):
        """
        Shows details of selected active plan or message that there is no such one.
        """
        user = request.user
        try:
            selected_plan = m.SelectedPlan.objects.get(user=user)
            plan = m.Plan.objects.get(id=selected_plan.active_plan_id)
            meals = m.Meal.objects.filter(plan=plan.id)
            return render(request, 'user_selected_plan.html', {'plan': plan, 'meals': meals})
        except ObjectDoesNotExist:
            msg = 'Nie masz wybranego aktualnego planu.'
            return render(request, 'user_selected_plan.html', {'msg': msg})


class UserSelectedPlanAddView(PermissionRequiredMixin, View):
    """
    Saves specific plan as user's active plan, only for logged in user.
    """
    permission_required = 'web_app.add_selectedplan'

    def get(self, request, plan_id):
        """
        Shows warning if user really wants to set the plan as an active plan.
        """
        plan = m.Plan.objects.get(id=plan_id)
        return render(request, 'user_selected_plan_add.html', {'plan': plan})

    def post(self, request, plan_id):
        """
        If answer is yes, saves specific plan as user's active plan, only one plan can be chosen at a time,
        then redirects to user active plan site. Otherwise redirects to plan details site.
        """
        user = request.user
        if request.POST.get('answer') == 'Tak':
            try:
                selected_plan = m.SelectedPlan.objects.get(user=user)
                selected_plan.active_plan_id = plan_id
                selected_plan.save()
            except ObjectDoesNotExist:
                m.SelectedPlan.objects.create(user=user, active_plan_id=plan_id)
            return redirect('user_active_plan')
        else:
            return redirect('plan_details', plan_id=plan_id)


def products_sort(product):
    """
    Function used to sort products first by type, then by name.
    """
    return product.type.name


class PlanProductListView(View):
    """
    Shows list of products from all meals included in specified plan.
    """
    def get(self, request, plan_id):
        """
        Show interactive list of products needed for the plan. List is made of two tables: 'Yet to buy'
        and 'Already bought'.
        """
        plan = m.Plan.objects.get(id=plan_id)
        meals = m.Meal.objects.filter(plan=plan)
        products_list = []
        cost = 0
        for meal in meals:
            products = m.Product.objects.filter(meal=meal)
            for product in products:
                products_list.append(product)
                cost += product.price
        products_list.sort(key=products_sort)
        return render(request, 'plan_product_list.html', {'plan': plan, 'meals': meals,
                                                          'products': products_list, 'cost': cost})
