from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Sum 
from datetime import date
from collections import defaultdict
from decimal import Decimal

from .models import *


# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return render(request, "expense/index.html")
    expenses = Expense.objects.filter(user = request.user).order_by('-date', '-time')
    incomes = Income.objects.filter(user = request.user).order_by('-date', '-time')
    total_expense = 0
    for expense in expenses:
        total_expense += expense.amount
    total_income = 0
    for income in incomes:
        total_income += income.amount
    
    categories = Category.objects.all()
    return render(request, "expense/index.html", {
        "categories": categories,
        "expenses": expenses[:5],
        "incomes": incomes[:5],
        "total_expense": total_expense,
        "total_income": total_income,
        "saving": total_income - total_expense,
    })


def expense(request):
    if not request.user.is_authenticated:
        return render(request, "expense/expense.html")
    expenses = Expense.objects.filter(user = request.user).order_by('-date', '-time')
    total_expense = 0
    for expense in expenses:
        total_expense += expense.amount
    
    categories = Category.objects.all()
    return render(request, "expense/expense.html", {
        "categories": categories,
        "expenses": expenses,
        "total_expense": total_expense
    })


def income(request):
    if not request.user.is_authenticated:
        return render(request, "expense/income.html")
    incomes = Income.objects.filter(user = request.user).order_by('-date', '-time')
    total_income = 0
    for income in incomes:
        total_income += income.amount
    
    return render(request, "expense/income.html", {
        "incomes": incomes,
        "total_income": total_income
    })


def budget(request):
    if not request.user.is_authenticated:
        return render(request, "expense/budget.html")
    categories = Category.objects.all()

    today = date.today()
    current_month = today.month
    current_year = today.year

    expenses = Expense.objects.filter(
        user=request.user,
        date__month=current_month,
        date__year=current_year
    ).values('category').annotate(total_amount=Sum('amount'))

    budgets = Budget.objects.filter(user = request.user).order_by('-category').reverse()
    return render(request, "expense/budget.html", {
        "categories": categories,
        "budgets": budgets,
        "expenses": expenses,
    })


def profile(request):
    
    categories = Category.objects.all()
    return render(request, "expense/profile.html", {
        "categories": categories,
    })


def get_data(request):
    if not request.user.is_authenticated:
        return JsonResponse({
        "message": "Not Signed In"
    })
    
    cat_data = Expense.objects.filter(user=request.user).values('category').annotate(total=Sum('amount'))
    
    cat_labels = [Category.objects.get(pk = x['category']).title for x in cat_data]
    cat_totals = [x['total'] for x in cat_data]

    expenses_by_date = Expense.objects.filter(user=request.user).values('date').annotate(total=Sum('amount')).order_by('date')
    dates = [e['date'].strftime('%Y-%m-%d') for e in expenses_by_date]
    totals = [e['total'] for e in expenses_by_date]

    expenses = Expense.objects.filter(user=request.user)
    incomes = Income.objects.filter(user=request.user)

    expense_months = [exp.date.strftime("%Y-%m") for exp in expenses]
    income_months = [inc.date.strftime("%Y-%m") for inc in incomes]
    months = sorted(set(expense_months + income_months))

    income_data = defaultdict(Decimal)
    expense_data = defaultdict(Decimal)

    for inc in incomes:
        income_data[inc.date.strftime("%Y-%m")] += inc.amount

    for exp in expenses:
        expense_data[exp.date.strftime("%Y-%m")] += exp.amount

    return JsonResponse({
        "message": "Data Recieved Successfully",
        "cat_labels": cat_labels, 
        "cat_totals": cat_totals,
        "line_dates": dates,
        "line_totals": totals,
        "months": months,
        "inc": [income_data[month] for month in months],
        "exp": [expense_data[month] for month in months],
    })


def add_expense(request):
    if request.method == "POST":
        name = request.POST["name"]
        amount = float(request.POST["amount"])
        category = request.POST["Category"]
        date = request.POST["date"]
        currUser = request.user
        cate = Category.objects.filter(title=category).first()
        expense = Expense(
            name = name,
            amount = amount,
            category = cate,
            user = currUser,
            date = date
        )
        expense.save()
        return HttpResponseRedirect(reverse("profile"))
    
    
def delete_expense(request, id):
    expense = Expense.objects.filter(pk = id).first()
    expense.delete()
    return JsonResponse({"message": "Expense Removed"})
    

def edit_expense(request, id):
    if request.method == "POST":
        expense = Expense.objects.filter(pk = id).first()
        name = request.POST["name"]
        amount = float(request.POST["amount"])
        category = request.POST["Category"]
        date = request.POST["date"]
        currUser = request.user
        cate = Category.objects.filter(title=category).first()
        expense.name = name
        expense.amount = amount
        expense.date = date
        expense.user = currUser
        expense.category = cate
        expense.save()
        return HttpResponseRedirect(reverse("expense"))


def add_income(request):
    if request.method == "POST":
        name = request.POST["name"]
        amount = float(request.POST["amount"])
        if (amount < 0):
            pass
        date = request.POST["date"]
        currUser = request.user
        income = Income(
            name = name,
            amount = amount,
            user = currUser,
            date = date
        )
        income.save()
        return HttpResponseRedirect(reverse("profile"))
    

def delete_income(request, id):
    income = Income.objects.filter(pk = id).first()
    income.delete()
    return JsonResponse({"message": "Income Removed"})


def edit_income(request, id):
    if request.method == "POST":
        income = Income.objects.filter(pk = id).first()
        name = request.POST["name"]
        amount = float(request.POST["amount"])
        date = request.POST["date"]
        currUser = request.user
        income.name = name
        income.date = date
        income.amount = amount
        income.user = currUser
        income.save()
        return HttpResponseRedirect(reverse("income"))
    

def set_budget(request):
    if request.method == "POST":
        categories = Category.objects.all()
        currUser = request.user
        for category in categories:
            amt = request.POST[category.title]

            if amt:
                amt = float(amt)
                Budget.objects.update_or_create(
                    user = currUser,
                    category = category,
                    defaults={'amount': amt}
                )
        return HttpResponseRedirect(reverse("profile")) 



def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "expense/index.html", {
                "message": "Invalid username and/or password."
            })
    

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "expense/index.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "expense/index.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))