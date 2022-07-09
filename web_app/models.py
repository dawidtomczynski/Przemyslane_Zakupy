from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models

# Create your models here.


def get_sentinel_user():
    """
    Function used to set products and meals creator as 'deleted' in case of user deletion.
    """
    return get_user_model().objects.get_or_create(username='deleted')[0]


TYPES = (
    (1, 'mięsny'),
    (2, 'wegetariański'),
    (3, 'wegański')
)


class Plan(models.Model):
    """
    Model specifying plan details.
    """
    name = models.CharField(max_length=64)
    date_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET(get_sentinel_user))
    meal = models.ManyToManyField('Meal', through='PlanMeal')
    type = models.IntegerField(choices=TYPES)
    persons = models.IntegerField()

    def __str__(self):
        """
        Function used to show plan by its name.
        """
        return self.name


class SelectedPlan(models.Model):
    """
    Model specifying relation between User and its active plan.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    active_plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True)


class FavouritePlan(models.Model):
    """
    Model specifying relations between User and its favourite plans.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ManyToManyField(Plan)


class PlanMeal(models.Model):
    """
    Model specifying relations between plans and meals.
    """
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    meal = models.ForeignKey('Meal', on_delete=models.CASCADE)


class Meal(models.Model):
    """
    Model specifying meal details.
    """
    name = models.CharField(max_length=64)
    date_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET(get_sentinel_user))
    recipe = models.TextField(blank=True)
    type = models.IntegerField(choices=TYPES)
    product = models.ManyToManyField('Product', through='MealProduct')

    def __str__(self):
        """
        Function used to show meal by its name.
        """
        return self.name


class FavouriteMeal(models.Model):
    """
    Model specifying relations between User and its favourite meals.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    meal = models.ManyToManyField(Meal)


class MealProduct(models.Model):
    """
    Model specifying relations between meals and products.
    """
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    grams = models.IntegerField(default=0)


class Product(models.Model):
    """
    Model specifying product details.
    """
    name = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    kcal = models.IntegerField()
    type = models.ForeignKey('ProductType', on_delete=models.CASCADE)

    def __str__(self):
        """
        Function used to show product by its name.
        """
        return self.name


class ProductType(models.Model):
    """
    Model specifying product type details.
    """
    name = models.CharField(max_length=64)

    def __str__(self):
        """
        Function used to show product type by its name.
        """
        return self.name
