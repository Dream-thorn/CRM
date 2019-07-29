from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import auth
from django.urls import reverse
from crm.forms import RegForm, CustomerForm
from crm import models
from utils.pagination import Pagination
from django.views import View


# 登录
def login(request):
    error_msg = ''

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # 验证用户名和密码
        obj = auth.authenticate(request, username=username, password=password)
        # print(obj)
        if obj:
            auth.login(request, obj)
            return redirect(reverse('my_customer'))
        error_msg = '用户名或密码错误'

    return render(request, 'login.html', {'error_msg': error_msg})


# 注销
def logout(request):
    auth.logout(request)

    return redirect('/login/')


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


"""
# 客户列表
def customer_list(request):
    # 如果要访问公有客户
    if request.path_info == reverse('customer'):
        # 公有客户信息
        all_customer = models.Customer.objects.filter(consultant__isnull=True)
    else:
        # 私有客户信息
        all_customer = models.Customer.objects.filter(consultant=request.user)

    # 分页功能
    page = Pagination(request, len(all_customer))

    return render(request, 'crm/customer_list.html',
                  {'all_customer': all_customer[page.data_start: page.data_end],
                   'all_tag': page.show_li,
                   'user': request.user})
"""


# 客户列表
class CustomerList(View):

    def get(self, request):
        # 要查询的字段
        query_list = ['qq', 'name', 'date']
        q = self.get_search_content(query_list)
        # 如果要访问公有客户
        if request.path_info == reverse('customer'):
            # 公有客户信息
            all_customer = models.Customer.objects.filter(q, consultant__isnull=True)
        else:
            # 私有客户信息
            all_customer = models.Customer.objects.filter(q, consultant=request.user)

        # print(request.GET)      # <QueryDict: {'query': ['user'], 'page': ['2']}>
        # print(request.GET.urlencode())      # query=user&page=2

        query_params = request.GET.copy()   # QueryDict的深拷贝方法


        # 分页功能
        page = Pagination(request, len(all_customer), query_params, each_page_data=2)

        return render(request, 'crm/customer_list.html',
                      {'all_customer': all_customer[page.data_start: page.data_end],
                       'all_tag': page.show_li,
                       'user': request.user})

    def post(self, request):
        # 获取用户选择的操作
        action = request.POST.get('action')
        # 用反射查看这个操作是否可执行
        if getattr(self, action):
            # 执行这个操作
            getattr(self, action)()

        return self.get(request)

    # 设为公有
    def public(self):
        # 获取客户钩选的用户的id
        ids = self.request.POST.getlist('id')

        # 多对一设为公有
        # models.Customer.objects.filter(id__in=ids).update(consultant=None)

        # 一对多设为公有
        self.request.user.customers.remove(*models.Customer.objects.filter(id__in=ids))

    # 设为私有
    def private(self):
        ids = self.request.POST.getlist('id')

        # 多对一设为私有
        # models.Customer.objects.filter(id__in=ids).update(consultant=self.request.user)

        # 一对多设为私有
        self.request.user.customers.add(*models.Customer.objects.filter(id__in=ids))

    # 删除用户
    def delete(self):
        ids = self.request.POST.getlist('id')
        models.Customer.objects.filter(id__in=ids).delete()

    # 模糊查询
    def get_search_content(self, query_list):
        query = self.request.GET.get('query', '')
        q = Q()
        q.connector = 'OR'
        for i in query_list:
            q.children.append(Q((f'{i}__contains', query)))

        # q = Q(Q((qq__contains, query)) | Q((name__contains, query)) | ...)
        return q


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

    return render(request, 'crm/customer_add_or_edit.html',
                  {'form_obj': form_obj,
                   'edit_id': edit_id,
                   'user': request.user})
