from django import template
from django.shortcuts import get_object_or_404

from web_app import models as m

register = template.Library()


@register.filter(name='kcal_count')
def kcal_count(arg):
    """
    Function used to count average kcal/100g for specified meal.
    """
    products = m.Product.objects.filter(meal=arg.id)
    total_kcal = []
    for product in products:
        total_kcal.append(product.kcal)
    if len(total_kcal) != 0:
        return int((sum(total_kcal)) / len(total_kcal))
    else:
        return 0


@register.filter(name='price_count')
def price_count(arg):
    """
    Function used to count total price of specified meal.
    """
    products = m.Product.objects.filter(meal=arg.id)
    cost = 0
    for product in products:
        cost += product.price
    return cost


@register.filter(name='weight_count')
def weight_count(arg):
    """
    Function used to count total weight of specified meal.
    """
    products = m.MealProduct.objects.filter(meal_id=arg.id)
    weight = 0
    for product in products:
        weight += product.grams
    return weight


@register.filter(name='plan_cost')
def plan_cost(arg):
    """
    Function used to count total price of specified plan.
    """
    cost = 0
    meals = m.PlanMeal.objects.filter(plan_id=arg.id)
    for meal in meals:
        products = m.Product.objects.filter(meal=meal.meal_id)
        for product in products:
            cost += product.price
    return cost
