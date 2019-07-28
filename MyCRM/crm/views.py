from django.shortcuts import render, redirect
from django.contrib import auth
from django.urls import reverse
from crm.forms import RegForm, CustomerForm
from crm import models
from utils.pagination import Pagination


# 登录
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


# 注册
def reg(request):
    reg_obj = RegForm()

    if request.method == 'POST':
        reg_obj = RegForm(request.POST)
        if reg_obj.is_valid():
            # 成功通过校验, 创建新用户

            # 方案一
            # reg_obj.cleaned_data.pop('re_password')
            # models.UserProfile.objects.create_user(**reg_obj.cleaned_data)

            # 方案二
            obj = reg_obj.save()  # 相当于使用create方法创建, 所以密码是明文
            obj.set_password(obj.password)  # 将密码重新设置为密文
            obj.save()

            return redirect('/login/')

    return render(request, 'reg.html', {'reg_obj': reg_obj})


# 客户列表
def customer_list(request):
    # 全部客户信息
    all_customer = models.Customer.objects.all()

    page = Pagination(request, len(all_customer))

    return render(request, 'crm/customer_list.html',
                  {'all_customer': all_customer[page.data_start: page.data_end], 'all_tag': page.show_li})


"""
# 添加客户
def customer_add(request):
    form_obj = CustomerForm()

    if request.method == 'POST':
        form_obj = CustomerForm(request.POST)
        if form_obj.is_valid():
            form_obj.save()

            return redirect(reverse('customer'))

    return render(request, 'crm/customer_add.html', {'form_obj': form_obj})


# 编辑客户
def customer_edit(request, edit_id):
    edit_obj = models.Customer.objects.filter(id=edit_id).first()
    form_obj = CustomerForm(instance=edit_obj)

    if request.method == 'POST':
        form_obj = CustomerForm(request.POST, instance=edit_obj)
        if form_obj.is_valid():
            form_obj.save()

            return redirect(reverse('customer'))

    return render(request, 'crm/customer_edit.html', {'form_obj': form_obj})
"""


# 添加编辑客户功能二合一
def customer_add_or_edit(request, edit_id=None):
    edit_obj = models.Customer.objects.filter(id=edit_id).first()
    form_obj = CustomerForm(instance=edit_obj)

    if request.method == 'POST':
        form_obj = CustomerForm(request.POST, instance=edit_obj)
        if form_obj.is_valid():
            form_obj.save()

            return redirect(reverse('customer'))

    return render(request, 'crm/customer_add_or_edit.html', {'form_obj': form_obj, 'edit_id': edit_id})
