from django.shortcuts import render, redirect
from django.contrib import auth


def login(request):
    error_msg = ''

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # 验证用户名和密码
        obj = auth.authenticate(request, username=username, password=password)
        print(obj)
        if obj:
            return redirect('/index/')
        error_msg = '用户名或密码错误'

    return render(request, 'login.html', {'error_msg': error_msg})
