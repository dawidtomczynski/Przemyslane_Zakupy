from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models

# Create your models here.


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]


TYPES = (
    (1, 'mięsny'),
    (2, 'wegetariański'),
    (3, 'wegański')
)


class Plan(models.Model):
    name = models.CharField(max_length=64)
    date_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET(get_sentinel_user))
    meal = models.ManyToManyField('Meal', through='PlanMeal')
    type = models.IntegerField(choices=TYPES)
    persons = models.IntegerField()

    def __str__(self):
        return self.name


class SelectedPlan(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    active_plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True)


class FavouritePlan(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ManyToManyField(Plan)


class PlanMeal(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    meal = models.ForeignKey('Meal', on_delete=models.CASCADE)


class Meal(models.Model):
    name = models.CharField(max_length=64)
    date_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET(get_sentinel_user))
    recipe = models.TextField(blank=True)
    type = models.IntegerField(choices=TYPES)
    product = models.ManyToManyField('Product', through='MealProduct')

    def __str__(self):
        return self.name


class FavouriteMeal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    meal = models.ManyToManyField(Meal)


class Product(models.Model):
    name = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    kcal = models.IntegerField()
    type = models.ForeignKey('ProductType', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class MealProduct(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    grams = models.IntegerField(default=0)


class ProductType(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name
