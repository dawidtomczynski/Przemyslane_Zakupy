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

    path('login/', v.LoginView.as_view()),
    path('register/', v.UserCreateView.as_view()),
    path('logout/', v.LogoutView.as_view()),
    path('profile/update/', v.UserUpdateView.as_view()),
    path('profile/update-password/', v.UserUpdatePasswordView.as_view()),
    path('profile/delete/', v.UserDeleteView.as_view()),


    path('', v.BaseView.as_view()),
    path('plans/', v.PlanListView.as_view()),
    path('plans/<int:plan_id>/', v.PlanDetailsView.as_view()),
    path('plans/add/', v.PlanAddView.as_view()),
    path('plans/edit/<int:plan_id>/', v.PlanModifyView.as_view()),
    path('plans/delete/<int:plan_id>/', v.PlanDeleteView.as_view()),
    path('plans/add-meal/<int:plan_id>', v.PlanMealAddView.as_view()),


    path('meals/', v.MealListView.as_view()),
    path('meals/<int:meal_id>', v.MealDetailsView.as_view()),
    path('meals/add/', v.MealAddView.as_view()),
    path('meals/edit/<int:meal_id>', v.MealModifyView.as_view()),
    path('meals/delete/<int:meal_id>', v.MealDeleteView.as_view()),
    path('meals/add-product/<int:meal_id>', v.MealProductAddView.as_view()),
    path('meals/add-plan/<int:meal_id>', v.MealPlanAddView.as_view()),
    path('meals/set-grams/<int:meal_id>/<int:product_id>', v.MealProductGramsSet.as_view()),


    path('products/', v.ProductListView.as_view()),
    path('products/<int:product_id>', v.ProductDetailsView.as_view()),
    path('products/add/', v.ProductAddView.as_view()),
    path('products/edit/<int:product_id>', v.ProductModifyView.as_view()),
    path('products/delete/<int:product_id>', v.ProductDeleteView.as_view()),
    path('products/types/', v.ProductTypeListView.as_view()),
    path('products/types/add/', v.ProductTypeAddView.as_view()),
    path('products/types/edit/<int:product_type_id>', v.ProductTypeModifyView.as_view()),
    path('products/types/delete/<int:product_type_id>', v.ProductTypeDeleteView.as_view()),






]
