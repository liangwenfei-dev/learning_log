from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required  # 导入装饰器
from .forms import RegisterForm, ProfileForm  # 导入两个表单
from .models import Profile  # 导入Profile模型

def register(request):
    if request.method != 'POST':
        form = RegisterForm()
    else:
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            # 注册成功立刻创建Profile，导航栏不会报错
            Profile.objects.create(user=user)
            login(request,user)
            return redirect('learning_logs:index')
    context = {'form': form}
    return render(request,'accounts/register.html',context)


@login_required
def profile(request):
    # ✅ 模型是大写Profile，变量叫user_profile，避免名字冲突（推荐）
    user_profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=user_profile)

    context = {
        "form": form,
        "profile": user_profile
    }
    return render(request,"accounts/profile.html",context)
