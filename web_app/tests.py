import pytest
from django.contrib.auth.models import User, Permission, Group
from django.urls import reverse
from web_app import models as m


@pytest.fixture
def group():
    group = Group.objects.create(name='testgroup')
    codenames = ['change_user', 'delete_user', 'view_user', 'add_meal', 'change_meal', 'delete_meal', 'view_meal',
                 'add_plan', 'change_plan', 'delete_plan', 'view_plan', 'add_selectedplan', 'change_selectedplan',
                 'delete_selectedplan', 'view_selectedplan', 'view_product', 'add_planmeal', 'change_planmeal',
                 'delete_planmeal', 'view_planmeal', 'add_mealproduct', 'change_mealproduct', 'delete_mealproduct',
                 'view_mealproduct', 'add_favouriteplan', 'change_favouriteplan', 'delete_favouriteplan',
                 'view_favouriteplan', 'add_favouritemeal',  'change_favouritemeal', 'delete_favouritemeal',
                 'view_favouritemeal']
    permissions = Permission.objects.filter(codename__in=codenames)
    group.permissions.set(permissions)
    return group


@pytest.fixture
def user(group):
    user = User.objects.create(username='testusername')
    user.set_password('testpassword')
    user.groups.add(group)
    user.save()
    return user


@pytest.fixture
def superuser():
    superuser = User.objects.create(username='testsuperusername')
    superuser.set_password('testpassword')
    superuser.is_staff = True
    superuser.is_superuser = True
    codenames = ['add_product', 'change_product', 'delete_product', 'view_product', 'add_producttype',
                 'change_producttype', 'delete_producttype', 'view_producttype']
    permissions = Permission.objects.filter(codename__in=codenames)
    superuser.user_permissions.set(permissions)
    superuser.save()
    return superuser


@pytest.fixture
def producttype():
    producttype = m.ProductType.objects.create(name='testproducttype')
    return producttype


@pytest.fixture
def producttypes():
    producttype1 = m.ProductType.objects.create(name='testproducttype1')
    producttype2 = m.ProductType.objects.create(name='testproducttype2')
    producttype3 = m.ProductType.objects.create(name='testproducttype3')
    producttypes = m.ProductType.objects.all()
    return producttypes


@pytest.fixture
def product(producttype):
    product = m.Product.objects.create(name='testproduct', price=10, kcal=100, type=producttype)
    return product


@pytest.fixture
def products(producttype):
    product1 = m.Product.objects.create(name='testproduct1', price=10, kcal=100, type=producttype)
    product2 = m.Product.objects.create(name='testproduct2', price=10, kcal=100, type=producttype)
    product3 = m.Product.objects.create(name='testproduct3', price=10, kcal=100, type=producttype)
    products = m.Product.objects.all()
    return products


@pytest.fixture
def meal(user):
    meal = m.Meal.objects.create(name='testmeal', user=user, type=1)
    return meal


@pytest.fixture
def meals(user):
    meal1 = m.Meal.objects.create(name='testmeal1', user=user, type=1)
    meal2 = m.Meal.objects.create(name='testmeal2', user=user, type=1)
    meal3 = m.Meal.objects.create(name='testmeal3', user=user, type=1)
    meals = m.Meal.objects.all()
    return meals


@pytest.fixture
def plan(user):
    plan = m.Plan.objects.create(name='testplan', user=user, type=1, persons=1)
    return plan


@pytest.fixture
def plans(user):
    plan1 = m.Plan.objects.create(name='testplan1', user=user, type=1, persons=1)
    plan2 = m.Plan.objects.create(name='testplan2', user=user, type=1, persons=1)
    plan3 = m.Plan.objects.create(name='testplan3', user=user, type=1, persons=1)
    plans = m.Plan.objects.all()
    return plans


@pytest.fixture
def mealproduct(meal, product):
    mealproduct = m.MealProduct.objects.create(meal=meal, product=product, grams=100)
    return mealproduct


@pytest.fixture
def planmeal(plan, meal):
    planmeal = m.PlanMeal.objects.create(plan=plan, meal=meal)
    return planmeal


@pytest.fixture
def favouriteplan(user, plan):
    favouriteplan = m.FavouritePlan.objects.create(user=user)
    favouriteplan.plan.add(plan)
    return favouriteplan


@pytest.fixture
def selectedplan(user, plan):
    selectedplan = m.SelectedPlan.objects.create(user=user, active_plan=plan)
    return selectedplan


@pytest.fixture
def favouritemeal(user, meal):
    favouritemeal = m.FavouriteMeal.objects.create(user=user)
    favouritemeal.meal.add(meal)
    return favouritemeal


@pytest.mark.django_db
def test_with_client(client):
    response = client.get('')
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_view(client, user):
    url = reverse('user_login')
    get_response = client.get(url)
    assert get_response.status_code == 200

    data = {'username': 'testusername', 'password': 'testpassword'}
    post_response = client.post(url, data)
    assert user.is_authenticated
    assert post_response.status_code in (200, 302)


@pytest.mark.django_db
def test_logout_view(client, user):
    client.force_login(user)
    url = reverse('user_logout')
    response = client.get(url)
    assert response.status_code == 302
    # assert response.context['user'].is_authenticated


@pytest.mark.django_db
def test_user_create_view(client, group):
    url = reverse('user_create')
    get_response = client.get(url)
    assert get_response.status_code == 200

    Group.objects.create(name='Client')
    username = 'testusername'
    testpassword = 'testpassword'
    data = {'username': username, 'password': testpassword, 'password2': testpassword}
    post_response = client.post(url, data)
    assert User.objects.get(username=username)
    assert post_response.status_code in (200, 302)


@pytest.mark.django_db
def test_user_update_view(client, user):
    client.force_login(user)
    url = reverse('user_update')
    get_response = client.get(url)
    assert get_response.status_code == 200
    assert get_response.context.get('user') == user

    data = {'username': 'newtestname'}
    post_response = client.post(url, data)
    assert post_response.status_code in (200, 302)
    assert User.objects.get(**data)


@pytest.mark.django_db
def test_user_update_password_view(client, user):
    client.force_login(user)
    url = reverse('user_update_password')
    get_response = client.get(url)
    assert get_response.status_code == 200
    assert get_response.context.get('user') == user

    old_password = user.password
    new_password = 'newtestpassword'
    data = {'password': old_password, 'new_password': new_password, 'new_password2': new_password}
    post_response = client.post(url, data)
    assert post_response.status_code in (200, 302)
    # assert user.check_password(new_password)


@pytest.mark.django_db
def test_user_delete_view(client, user):
    client.force_login(user)
    url = reverse('user_delete')
    count_before_delete = User.objects.count()
    get_response = client.get(url)
    count_after_delete = User.objects.count()
    assert get_response.status_code in (200, 302)
    assert len(User.objects.filter(id=user.id)) == 0
    assert count_after_delete == count_before_delete - 1


@pytest.mark.django_db
def test_plan_list_view(client, plans):
    url = reverse('plans')
    get_response = client.get(url)
    plans = m.Plan.objects.all()
    assert get_response.status_code == 200
    assert list(get_response.context.get('plans')) == list(plans)


@pytest.mark.django_db
def test_plan_details_view(client, plan, meals):
    url = reverse('plan_details', args=(plan.id,))
    plan.meal.set(meals)
    get_response = client.get(url)
    assert get_response.status_code == 200
    assert get_response.context.get('plan') == plan
    assert list(get_response.context.get('meals')) == list(meals)


@pytest.mark.django_db
def test_plan_add_view(client, user):
    client.force_login(user)
    url = reverse('plan_add')
    get_response = client.get(url)
    assert get_response.status_code == 200

    data = {'name': 'testplan', 'type': 1, 'persons': 1}
    count_before_add = m.Plan.objects.count()
    post_response = client.post(url, data)
    count_after_add = m.Plan.objects.count()
    assert post_response.status_code in (200, 302)
    assert m.Plan.objects.get(**data)
    assert count_after_add == count_before_add + 1


@pytest.mark.django_db
def test_plan_modify_view(client, user, plan):
    client.force_login(user)
    url = reverse('plan_modify', args=(plan.id,))
    get_response = client.get(url)
    assert get_response.status_code == 200

    data = {'name': 'newplanname', 'type': 3, 'persons': 3}
    count_before_modify = m.Plan.objects.count()
    post_response = client.post(url, data)
    count_after_modify = m.Plan.objects.count()
    assert post_response.status_code in (200, 302)
    assert m.Plan.objects.get(**data)
    assert m.Plan.objects.get(**data).id == plan.id
    assert count_after_modify == count_before_modify


@pytest.mark.django_db
def test_plan_delete_view(client, user, plan):
    client.force_login(user)
    url = reverse('plan_delete', args=(plan.id,))
    get_response = client.get(url)
    assert get_response.status_code in (200, 302)
    assert get_response.context.get('plan') == plan

    data = {'answer': 'Tak'}
    count_before_delete = m.Plan.objects.count()
    post_response = client.post(url, data)
    count_after_delete = m.Plan.objects.count()
    assert post_response.status_code in (200, 302)
    assert m.Plan.objects.filter(id=plan.id).count() == 0
    assert count_after_delete == count_before_delete - 1


@pytest.mark.django_db
def test_plan_meal_add_view(client, user, plan, meals):
    client.force_login(user)
    url = reverse('plan_meal_add', args=(plan.id,))
    get_response = client.get(url)
    assert get_response.status_code == 200
    assert get_response.context.get('plan') == plan

    data = {'meal': [meal.id for meal in meals]}
    post_response = client.post(url, data)
    assert post_response.status_code in (200, 302)
    assert m.PlanMeal.objects.filter(plan_id=plan.id).count() == 3


@pytest.mark.django_db
def test_plan_meal_random_add_view(client, user, plan, meals):
    client.force_login(user)
    url = reverse('plan_meal_random_add', args=(plan.id,))
    count_before_add = plan.meal.count()
    get_response = client.get(url)
    count_after_add = plan.meal.count()
    assert get_response.status_code in (200, 302)
    assert count_after_add == count_before_add + 1


@pytest.mark.django_db
def test_meal_list_view(client):
    url = reverse('meals')
    get_response = client.get(url)
    meals = m.Meal.objects.all()
    assert get_response.status_code == 200
    assert list(get_response.context.get('meals')) == list(meals)


@pytest.mark.django_db
def test_meal_details_view(client, meal, products):
    url = reverse('meal_details', args=(meal.id,))
    meal.product.set(products)
    get_response = client.get(url)
    assert get_response.status_code == 200
    assert get_response.context.get('meal') == meal
    assert list(get_response.context.get('products')) == list(products)


@pytest.mark.django_db
def test_meal_add_view(client, user):
    client.force_login(user)
    url = reverse('meal_add')
    get_response = client.get(url)
    assert get_response.status_code == 200

    data = {'name': 'testmeal', 'type': 1}
    count_before_add = m.Meal.objects.count()
    post_response = client.post(url, data)
    count_after_add = m.Meal.objects.count()
    assert post_response.status_code in (200, 302)
    assert m.Meal.objects.get(**data)
    assert count_after_add == count_before_add + 1


@pytest.mark.django_db
def test_meal_modify_view(client, user, meal):
    client.force_login(user)
    url = reverse('meal_modify', args=(meal.id,))
    get_response = client.get(url)
    assert get_response.status_code == 200

    data = {'name': 'newmealname', 'type': 3}
    count_before_modify = m.Meal.objects.count()
    post_response = client.post(url, data)
    count_after_modify = m.Meal.objects.count()
    assert post_response.status_code in (200, 302)
    assert m.Meal.objects.get(**data)
    assert m.Meal.objects.get(**data).id == meal.id
    assert count_after_modify == count_before_modify


@pytest.mark.django_db
def test_meal_delete_view(client, user, meal):
    client.force_login(user)
    url = reverse('meal_delete', args=(meal.id,))
    get_response = client.get(url)
    assert get_response.status_code in (200, 302)
    assert get_response.context.get('meal') == meal

    data = {'answer': 'Tak'}
    count_before_delete = m.Meal.objects.count()
    post_response = client.post(url, data)
    count_after_delete = m.Meal.objects.count()
    assert post_response.status_code in (200, 302)
    assert m.Meal.objects.filter(id=meal.id).count() == 0
    assert count_after_delete == count_before_delete - 1


@pytest.mark.django_db
def test_meal_plan_add_view(client, user, meal, plans):
    client.force_login(user)
    url = reverse('meal_plan_add', args=(meal.id,))
    get_response = client.get(url)
    assert get_response.status_code == 200
    assert get_response.context.get('meal') == meal

    data = {'plan': [plan.id for plan in plans]}
    post_response = client.post(url, data)
    assert post_response.status_code in (200, 302)
    assert m.PlanMeal.objects.filter(meal_id=meal.id).count() == 3


@pytest.mark.django_db
def test_meal_product_add_view(client, user, meal, products):
    client.force_login(user)
    url = reverse('meal_product_add', args=(meal.id,))
    get_response = client.get(url)
    assert get_response.status_code == 200
    assert get_response.context.get('meal') == meal

    data = {'product': [product.id for product in products]}
    post_response = client.post(url, data)
    assert post_response.status_code in (200, 302)
    assert m.MealProduct.objects.filter(meal_id=meal.id).count() == 3


@pytest.mark.django_db
def test_meal_grams_set_view(client, user, meal, product):
    client.force_login(user)
    meal.product.add(product)
    url = reverse('meal_grams', args=(meal.id, product.id,))
    get_response = client.get(url)
    assert get_response.status_code == 200

    data = {'grams': 200}
    post_response = client.post(url, data)
    obj = m.MealProduct.objects.get(meal=meal, product=product)
    assert post_response.status_code in (200, 302)
    assert obj.grams == 200


@pytest.mark.django_db
def test_product_list_view(client):
    url = reverse('products')
    get_response = client.get(url)
    products = m.Product.objects.all()
    assert get_response.status_code == 200
    assert list(get_response.context.get('products')) == list(products)


@pytest.mark.django_db
def test_product_details_view(client, product):
    url = reverse('product_details', args=(product.id,))
    get_response = client.get(url)
    assert get_response.context.get('product') == product
    assert get_response.status_code == 200


@pytest.mark.django_db
def test_product_add_view(client, superuser, producttype):
    client.force_login(superuser)
    url = reverse('product_add')
    get_response = client.get(url)
    assert get_response.status_code == 200

    data = {'name': 'testproduct', 'price': 10, 'kcal': 100, 'type': producttype.id}
    count_before_add = m.Product.objects.count()
    post_response = client.post(url, data)
    count_after_add = m.Product.objects.count()
    assert post_response.status_code in (200, 302)
    assert m.Product.objects.get(**data)
    assert count_after_add == count_before_add + 1


@pytest.mark.django_db
def test_product_modify_view(client, superuser, product, producttype):
    client.force_login(superuser)
    url = reverse('product_modify', args=(product.id,))
    get_response = client.get(url)
    assert get_response.status_code == 200

    data = {'name': 'newproductname', 'price': 20, 'kcal': 200, 'type': producttype.id}
    count_before_modify = m.Product.objects.count()
    post_response = client.post(url, data)
    count_after_modify = m.Product.objects.count()
    assert post_response.status_code in (200, 302)
    assert m.Product.objects.get(**data)
    assert m.Product.objects.get(**data).id == product.id
    assert count_after_modify == count_before_modify


@pytest.mark.django_db
def test_product_delete_view(client, superuser, product):
    client.force_login(superuser)
    url = reverse('product_delete', args=(product.id,))
    get_response = client.get(url)
    assert get_response.status_code in (200, 302)
    assert get_response.context.get('product') == product

    data = {'answer': 'Tak'}
    count_before_delete = m.Product.objects.count()
    post_response = client.post(url, data)
    count_after_delete = m.Product.objects.count()
    assert post_response.status_code in (200, 302)
    assert m.Product.objects.filter(id=product.id).count() == 0
    assert count_after_delete == count_before_delete - 1


@pytest.mark.django_db
def test_product_type_list_view(client, superuser, producttypes):
    client.force_login(superuser)
    url = reverse('product_types')
    get_response = client.get(url)
    product_types = m.ProductType.objects.all()
    assert get_response.status_code == 200
    assert list(get_response.context.get('product_types')) == list(product_types)


@pytest.mark.django_db
def test_product_type_add_view(client, superuser):
    client.force_login(superuser)
    url = reverse('product_type_add')
    get_response = client.get(url)
    assert get_response.status_code == 200

    data = {'name': 'testproducttype'}
    count_before_add = m.ProductType.objects.count()
    post_response = client.post(url, data)
    count_after_add = m.ProductType.objects.count()
    assert post_response.status_code in (200, 302)
    assert m.ProductType.objects.get(**data)
    assert count_after_add == count_before_add + 1


@pytest.mark.django_db
def test_product_type_modify_view(client, superuser, producttype):
    client.force_login(superuser)
    url = reverse('product_type_modify', args=(producttype.id,))
    get_response = client.get(url)
    assert get_response.status_code == 200

    data = {'name': 'newproducttypename'}
    count_before_modify = m.ProductType.objects.count()
    post_response = client.post(url, data)
    count_after_modify = m.ProductType.objects.count()
    assert post_response.status_code in (200, 302)
    assert m.ProductType.objects.get(**data)
    assert m.ProductType.objects.get(**data).id == producttype.id
    assert count_after_modify == count_before_modify


@pytest.mark.django_db
def test_product_type_delete_view(client, superuser, producttype):
    client.force_login(superuser)
    url = reverse('product_type_delete', args=(producttype.id,))
    get_response = client.get(url)
    assert get_response.status_code in (200, 302)
    assert get_response.context.get('product_type') == producttype

    data = {'answer': 'Tak'}
    count_before_delete = m.ProductType.objects.count()
    post_response = client.post(url, data)
    count_after_delete = m.ProductType.objects.count()
    assert post_response.status_code in (200, 302)
    assert m.ProductType.objects.filter(id=producttype.id).count() == 0
    assert count_after_delete == count_before_delete - 1


@pytest.mark.django_db
def test_user_plan_list_view(client, user, plans):
    client.force_login(user)
    url = reverse('user_plans')
    user_plans = m.Plan.objects.filter(user=user)
    get_response = client.get(url)
    assert get_response.status_code == 200
    assert list(get_response.context.get('user_plans')) == list(user_plans)


@pytest.mark.django_db
def test_user_favourite_plan_list_view(client, user, plans):
    client.force_login(user)
    favourite_user_plan = m.FavouritePlan.objects.create(user=user)
    favourite_user_plan.plan.set(plans)
    url = reverse('user_favourite_plans')
    favourite_plans = m.Plan.objects.filter(favouriteplan__user=user)
    get_response = client.get(url)
    assert get_response.status_code == 200
    assert list(get_response.context.get('favourite_plans')) == list(favourite_plans)


@pytest.mark.django_db
def test_user_favourite_plan_add_view(client, user, plan):
    client.force_login(user)
    url = reverse('user_favourite_plan_add', args=(plan.id,))
    count_before_add = m.FavouritePlan.objects.filter(user=user).count()
    get_response = client.get(url)
    count_after_add = m.FavouritePlan.objects.filter(user=user).count()
    assert get_response.status_code in (200, 302)
    assert m.FavouritePlan.objects.get(user=user, plan=plan)
    assert count_after_add == count_before_add + 1


@pytest.mark.django_db
def test_user_favourite_plan_delete_view(client, user, plan, favouriteplan):
    client.force_login(user)
    url = reverse('user_favourite_plan_delete', args=(plan.id,))
    count_before_add = m.FavouritePlan.objects.filter(user=user, plan=plan).count()
    get_response = client.get(url)
    count_after_add = m.FavouritePlan.objects.filter(user=user, plan=plan).count()
    assert get_response.status_code in (200, 302)
    assert m.FavouritePlan.objects.filter(user=user, plan=plan).count() == 0
    assert count_after_add == count_before_add - 1


@pytest.mark.django_db
def test_user_meal_list_view(client, user, meals):
    client.force_login(user)
    url = reverse('user_meals')
    user_meals = m.Meal.objects.filter(user=user)
    get_response = client.get(url)
    assert get_response.status_code == 200
    assert list(get_response.context.get('user_meals')) == list(user_meals)


@pytest.mark.django_db
def test_user_favourite_meal_list_view(client, user, meals):
    client.force_login(user)
    favourite_user_meal = m.FavouriteMeal.objects.create(user=user)
    favourite_user_meal.meal.set(meals)
    url = reverse('user_favourite_meals')
    favourite_meals = m.Meal.objects.filter(favouritemeal__user=user)
    get_response = client.get(url)
    assert get_response.status_code == 200
    assert list(get_response.context.get('favourite_meals')) == list(favourite_meals)


@pytest.mark.django_db
def test_user_favourite_meal_add_view(client, user, meal):
    client.force_login(user)
    url = reverse('user_favourite_meal_add', args=(meal.id,))
    count_before_add = m.FavouriteMeal.objects.filter(user=user).count()
    get_response = client.get(url)
    count_after_add = m.FavouriteMeal.objects.filter(user=user).count()
    assert get_response.status_code in (200, 302)
    assert m.FavouriteMeal.objects.get(user=user, meal=meal)
    assert count_after_add == count_before_add + 1


@pytest.mark.django_db
def test_user_favourite_meal_delete_view(client, user, meal, favouritemeal):
    client.force_login(user)
    url = reverse('user_favourite_meal_delete', args=(meal.id,))
    count_before_add = m.FavouriteMeal.objects.filter(user=user, meal=meal).count()
    get_response = client.get(url)
    count_after_add = m.FavouriteMeal.objects.filter(user=user, meal=meal).count()
    assert get_response.status_code in (200, 302)
    assert m.FavouriteMeal.objects.filter(user=user, meal=meal).count() == 0
    assert count_after_add == count_before_add - 1


@pytest.mark.django_db
def test_user_selected_plan_view(client, user, plan, selectedplan):
    client.force_login(user)
    url = reverse('user_active_plan')
    get_response = client.get(url)
    assert get_response.status_code == 200
    assert get_response.context.get('plan') == plan


@pytest.mark.django_db
def test_user_selected_plan_add_view(client, user, plan):
    client.force_login(user)
    url = reverse('user_active_plan_add', args=(plan.id,))
    get_response = client.get(url)
    assert get_response.status_code == 200
    assert get_response.context.get('plan') == plan


@pytest.mark.django_db
def test_plan_product_list_view(client, plan, meal, planmeal, products):
    meal.product.set(products)
    url = reverse('plan_products', args=(plan.id,))
    get_response = client.get(url)
    assert get_response.status_code == 200
    assert get_response.context.get('plan') == plan
    assert list(get_response.context.get('products')) == list(products)
