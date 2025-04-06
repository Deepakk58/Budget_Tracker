from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("expense", views.expense, name="expense"),
    path("income", views.income, name="income"),
    path("budget", views.budget, name="budget"),
    path("profile", views.profile, name="profile"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add_expense", views.add_expense, name="add_expense"),
    path("delete_expense/<int:id>", views.delete_expense, name="delete_expense"),
    path("edit_expense/<int:id>", views.edit_expense, name="edit_expense"),
    path("add_income", views.add_income, name="add_income"),
    path("delete_income/<int:id>", views.delete_income, name="delete_income"),
    path("edit_income/<int:id>", views.edit_income, name="edit_income"),
    path("set_budget", views.set_budget, name="set_budget"),
    path("get_data", views.get_data, name="get_data")
]