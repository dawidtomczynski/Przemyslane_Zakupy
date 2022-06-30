from django import template
from web_app import models as m

register = template.Library()


@register.filter(name='kcal_count')
def kcal_count(arg):
    products = m.Product.objects.filter(meal=arg.id)
    total_kcal = []
    for product in products:
        total_kcal.append(product.kcal)
    return int((sum(total_kcal)) / len(total_kcal))


@register.filter(name='price_count')
def price_count(arg):
    products = m.Product.objects.filter(meal=arg.id)
    cost = 0
    for product in products:
        cost += product.price
    return cost


@register.filter(name='weight_count')
def weight_count(arg):
    products = m.MealProduct.objects.filter(meal_id=arg.id)
    weight = 0
    for product in products:
        weight += product.grams
    return weight


@register.filter(name='plan_cost')
def plan_cost(arg):
    meals = m.PlanMeal.objects.filter(plan_id=arg.id)
    cost = 0
    for meal in meals:
        products = m.MealProduct.objects.filter(meal_id=meal.id)
        for product in products.iterator():
            p = m.Product.objects.get(id=product.product_id)
            cost += p.price
    return cost
