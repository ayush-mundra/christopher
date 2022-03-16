from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import auth


def home(request):
    
    return render(request,'accounts/dashboard.html')
def calculate(request):
    data = request.POST.get('company_name')
    print(data)

    # return HttpResponse("working")
    return render(request,'accounts/dashboard.html')

