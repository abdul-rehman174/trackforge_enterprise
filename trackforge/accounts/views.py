from django.shortcuts import render,redirect,HttpResponse
from .models import CustomUser
from .forms import CustomUserForm



def user_list(request):
    users = CustomUser.objects.all()
    return render(request,"user_list.html",{"users":users})

def create_user(request):
    if request.method == "POST":
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/accounts/user_list")

    else:
        form = CustomUserForm()
    return render(request,"create_user.html",{"form":form ,"button_label":"Create"})

def update_user(request,pk):
    user = CustomUser.objects.get(pk=pk)
    if request.method == "POST":
        form = CustomUserForm(request.POST,instance = user)
        if form.is_valid():
            form.save()
            return redirect("/accounts/user_list")
    else:
        form = CustomUserForm(instance = user)
        return render(request,"create_user.html",{"form":form, "button_label":"Update"})


def delete_user(request, pk):
    user = CustomUser.objects.get(pk=pk)

    if request.method == "POST":
        user.delete()
        return redirect("/accounts/user_list")
    else:
        return render(request,"delete_user.html",{"user":user})


