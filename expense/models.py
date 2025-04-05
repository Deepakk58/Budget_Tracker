from django.contrib.auth.models import AbstractUser
from django.db import models

#Create Your Models here

class User(AbstractUser):
    pass


class Category(models.Model):
    title = models.CharField(max_length=100, unique=True)


class Expense(models.Model):
    user = models.ForeignKey(User, related_name="expenses", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    category = models.ForeignKey(Category, related_name="expenses", on_delete=models.CASCADE, blank=True, null=True)
    time = models.TimeField(auto_now_add=True)
    

class Income(models.Model):
    user = models.ForeignKey(User, related_name="incomes", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    time = models.TimeField(auto_now_add=True)


class Budget(models.Model):
    user = models.ForeignKey(User, related_name="budget", on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name="budget", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)