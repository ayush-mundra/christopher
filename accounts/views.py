from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import auth

def signup(request):
    if request.method == "POST":
        if request.POST['password1'] == request.POST['password2']:
            try:
                User.objects.get(username = request.POST['username'])
                return render (request,'accounts/signup.html', {'error':'Username is already taken!'})
            except User.DoesNotExist:
                user = User.objects.create_user(request.POST['username'],password=request.POST['password1'])
                auth.login(request,user)
                return redirect('home')
        else:
            return render (request,'accounts/signup.html', {'error':'Password does not match!'})
    else:
        return render(request,'accounts/signup.html') 

def login(request):
    print("inside login")

    try:
        user = auth.authenticate(username=request.GET['username'],password = request.GET['password'])
        print("user")
        print(user)
        if user is not None:
            auth.login(request,user)
            return redirect('home')
        else:
            return render (request,'accounts/login.html', {'error':'Username or password is incorrect!'})
    except:
        return render(request,'accounts/Login.html')
def check(request):

    print("inside")
    print(request.method)
    # print(request.status)

        # print()
    if request.method == 'GET':
        print("inside post")
        user = auth.authenticate(username=request.GET['username'],password = request.GET['password'])
        print("user")
        print(user)
        if user is not None:
            auth.login(request,user)
            return redirect('home')
        else:
            return render (request,'accounts/login.html', {'error':'Username or password is incorrect!'})
    else:
        return render(request,'accounts/Login.html')

def logout(request):
    if request.method == 'GET':
        print("inside post")

        auth.logout(request)
    return redirect('home')