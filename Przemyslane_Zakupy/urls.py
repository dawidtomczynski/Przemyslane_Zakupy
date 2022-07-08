"""Przemyslane_Zakupy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from web_app import views as v


urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', v.LoginView.as_view(), name='user_login'),
    path('register/', v.UserCreateView.as_view(), name='user_create'),
    path('logout/', v.LogoutView.as_view(), name='user_logout'),
    path('profile/update/', v.UserUpdateView.as_view(), name='user_update'),
    path('profile/update-password/', v.UserUpdatePasswordView.as_view(), name='user_update_password'),
    path('profile/delete/', v.UserDeleteView.as_view(), name='user_delete'),
    path('profile/plans/', v.UserPlanListView.as_view(), name='user_plans'),
    path('profile/favourite-plans/', v.UserFavouritePlanListView.as_view(), name='user_favourite_plans'),
    path('profile/favourite-plans/<int:plan_id>', v.UserFavouritePlanAddView.as_view(), name='user_favourite_plan_add'),
    path('profile/favourite-plans/delete/<int:plan_id>', v.UserFavouritePlanDeleteView.as_view(), name='user_favourite_plan_delete'),
    path('profile/meals/', v.UserMealList.as_view(), name='user_meals'),
    path('profile/favourite-meals/', v.UserFavouriteMealListView.as_view(), name='user_favourite_meals'),
    path('profile/favourite-meals/<int:meal_id>', v.UserFavouriteMealAddView.as_view(), name='user_favourite_meal_add'),
    path('profile/favourite-meals/delete/<int:meal_id>', v.UserFavouriteMealDeleteView.as_view(), name='user_favourite_meal_delete'),
    path('profile/active-plan/', v.UserSelectedPlanView.as_view(), name='user_active_plan'),
    path('profile/active-plan/<int:plan_id>', v.UserSelectedPlanAddView.as_view(), name='user_active_plan_add'),


    path('', v.BaseView.as_view(), name='base_view'),
    path('plans/', v.PlanListView.as_view(), name='plans'),
    path('plans/<int:plan_id>/', v.PlanDetailsView.as_view(), name='plan_details'),
    path('plans/add/', v.PlanAddView.as_view(), name='plan_add'),
    path('plans/edit/<int:plan_id>/', v.PlanModifyView.as_view(), name='plan_modify'),
    path('plans/delete/<int:plan_id>/', v.PlanDeleteView.as_view(), name='plan_delete'),
    path('plans/add-meal/<int:plan_id>', v.PlanMealAddView.as_view(), name='plan_meal_add'),
    path('plans/add-meal-random/<int:plan_id>', v.PlanMealRandomAdd.as_view(), name='plan_meal_random_add'),
    path('plans/product-list/<int:plan_id>', v.PlanProductListView.as_view(), name='plan_products'),




    path('meals/', v.MealListView.as_view(), name='meals'),
    path('meals/<int:meal_id>', v.MealDetailsView.as_view(), name='meal_details'),
    path('meals/add/', v.MealAddView.as_view(), name='meal_add'),
    path('meals/edit/<int:meal_id>', v.MealModifyView.as_view(), name='meal_modify'),
    path('meals/delete/<int:meal_id>', v.MealDeleteView.as_view(), name='meal_delete'),
    path('meals/add-product/<int:meal_id>', v.MealProductAddView.as_view(), name='meal_product_add'),
    path('meals/add-plan/<int:meal_id>', v.MealPlanAddView.as_view(), name='meal_plan_add'),
    path('meals/set-grams/<int:meal_id>/<int:product_id>', v.MealProductGramsSet.as_view(), name='meal_grams'),


    path('products/', v.ProductListView.as_view(), name='products'),
    path('products/<int:product_id>', v.ProductDetailsView.as_view(), name='product_details'),
    path('products/add/', v.ProductAddView.as_view(), name='product_add'),
    path('products/edit/<int:product_id>', v.ProductModifyView.as_view(), name='product_modify'),
    path('products/delete/<int:product_id>', v.ProductDeleteView.as_view(), name='product_delete'),
    path('products/types/', v.ProductTypeListView.as_view(), name='product_types'),
    path('products/types/add/', v.ProductTypeAddView.as_view(), name='product_type_add'),
    path('products/types/edit/<int:product_type_id>', v.ProductTypeModifyView.as_view(), name='product_type_modify'),
    path('products/types/delete/<int:product_type_id>', v.ProductTypeDeleteView.as_view(), name='product_type_delete'),


]
