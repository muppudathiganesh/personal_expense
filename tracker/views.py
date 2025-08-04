from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from .forms import RegisterForm, ExpenseForm
from .models import Expense
from django.db.models import Sum
from datetime import date


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'tracker/register.html', {'form': form})

@login_required
def dashboard(request):
    today = date.today()
    month_expenses = Expense.objects.filter(
        user=request.user,
        date__month=today.month,
        date__year=today.year
    )
    total = month_expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    category_breakdown = (
        month_expenses
        .values('category')
        .annotate(total=Sum('amount'))
    )

    return render(request, 'tracker/dashboard.html', {
        'total': total,
        'category_breakdown': category_breakdown,
        'expenses': month_expenses
    })

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm()
    return render(request, 'tracker/add_expense.html', {'form': form})

@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    form = ExpenseForm(request.POST or None, instance=expense)
    if form.is_valid():
        form.save()
        return redirect('dashboard')
    return render(request, 'tracker/edit_expense.html', {'form': form})

@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    expense.delete()
    return redirect('dashboard')

@user_passes_test(lambda u: u.is_superuser)
def admin_panel(request):
    expenses = Expense.objects.select_related('user').order_by('-date')
    return render(request, 'tracker/admin_dashboard.html', {'expenses': expenses})

@login_required
def all_expenses(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'tracker/all_expenses.html', {'expenses': expenses})