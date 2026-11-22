from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterForm

def register(request):
    if request.method != 'POST':
        form = RegisterForm()
    else:
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('learning_logs:index')
    context = {'form': form}
    return render(request,'accounts/register.html',context)



