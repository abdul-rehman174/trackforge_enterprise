from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CustomUserForm, SignupForm
from .models import CustomUser


def register_user(request):
    """Public self-signup. Authenticated admins can also use this to create
    plain users; for elevated roles they should use the Django admin."""
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account created for {user.username}. Please sign in.")
            return redirect("login")
    else:
        form = SignupForm()
    return render(request, "accounts/register_user.html", {
        "form": form,
        "button_label": "Create Account",
        "is_signup": True,
    })


def login(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""
        user = auth.authenticate(request, username=username, password=password)
        if user:
            auth.login(request, user)
            return redirect("/")
        messages.error(request, "Invalid username or password.")
    return render(request, "login.html")


def logout(request):
    auth.logout(request)
    return redirect("login")


@login_required
def user_list(request):
    users = CustomUser.objects.all().order_by("id")
    return render(request, "accounts/user_list.html", {"users": users})


@login_required
@permission_required("accounts.change_customuser", raise_exception=True)
def update_user(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == "POST":
        form = CustomUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"User '{user.username}' updated.")
            return redirect("user_list")
    else:
        form = CustomUserForm(instance=user)
    return render(request, "accounts/register_user.html", {
        "form": form,
        "button_label": "Update User",
        "is_signup": False,
    })


@login_required
@permission_required("accounts.delete_customuser", raise_exception=True)
def delete_user(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == "POST":
        user.delete()
        messages.success(request, "User deleted.")
        return redirect("user_list")
    return render(request, "accounts/delete_user.html", {"user": user})
