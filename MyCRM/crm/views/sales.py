from django.db import transaction
from django.db.models import Q
from django.http import QueryDict
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import auth
from django.urls import reverse
from crm.forms import RegForm, CustomerForm, ConsultRecordForm, EnrollmentForm
from crm import models
from utils.pagination import Pagination
from django.views import View
from django.conf import settings


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

        query_params = request.GET.copy()  # QueryDict的深拷贝方法

        # 分页功能
        page = Pagination(request, len(all_customer), query_params, each_page_data=10)

        # 下一个要跳转的url地址
        next_url = self.get_next().urlencode()  # next=%2Fcrm%2Fcustomer_list%2F%3Fquery%3Duser%26page%3D2

        return render(request, 'crm/sales/customer_list.html',
                      {'all_customer': all_customer[page.data_start: page.data_end],
                       'all_tag': page.show_li,
                       'user': request.user,
                       'next': next_url})

    def post(self, request):
        # 获取用户选择的操作
        action = request.POST.get('action')
        # 用反射查看这个操作是否可执行
        if getattr(self, action):
            # 执行这个操作
            ret = getattr(self, action)()

            if ret:
                return ret

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
        # 要设为私有的客户
        ids = self.request.POST.getlist('id')

        # 如果当前用户的私有客户数量加上要设为私有客户的数量大于setting.py中设置的值
        if self.request.user.customers.count() + len(ids) > settings.CUSTOMER_MAX_NUM:
            return HttpResponse("已经够多了, 不能太贪心哦")

        # 多对一设为私有
        # models.Customer.objects.filter(id__in=ids).update(consultant=self.request.user)
        # 一对多设为私有
        # self.request.user.customers.add(*models.Customer.objects.filter(id__in=ids))

        # 开始事务
        with transaction.atomic():
            # 加行级锁
            obj_list = models.Customer.objects.filter(id__in=ids, consultant__isnull=True).select_for_update()
            # 如果客户没有被抢走
            if len(ids) == len(obj_list):
                obj_list.update(consultant=self.request.user)
            else:
                return HttpResponse("客户被抢走了{}个, 请重新提交!".format(len(ids) - len(obj_list)))

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

    # 获取添加和编辑按钮当前页面的url
    def get_next(self):
        # 获取当前页面的全路径, 包含get参数, 如: /crm/customer_list/?query=user&page=2
        next_url = self.request.get_full_path()

        # 创建QueryDict字典
        qDict = QueryDict()
        # 将这个字典设为可修改
        qDict._mutable = True
        qDict['next'] = next_url

        return qDict


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

        # 获取要跳转的地址
        next_url = request.GET.get('next')
        if next_url:
            # 跳转到这个地址
            return redirect(next_url)

        return redirect(reverse('customer'))

    return render(request, 'crm/sales/customer_add_or_edit.html',
                  {'form_obj': form_obj,
                   'edit_id': edit_id,
                   'user': request.user})


# 咨询记录列表
class ConsultRecordList(View):

    def get(self, request, customer_id):
        # customer_id为0则查询当前用户的全部咨询记录
        if customer_id == '0':
            all_consult_record = models.ConsultRecord.objects.filter(consultant=request.user, delete_status=False)
        # 否则查询当前用户的客户id为customer_id的咨询记录
        else:
            all_consult_record = models.ConsultRecord.objects.filter(customer_id=customer_id, consultant=request.user,
                                                                     delete_status=False)

        query_params = request.GET.copy()
        # 分页功能
        page = Pagination(request, len(all_consult_record), query_params, each_page_data=10)

        return render(request, 'crm/sales/consult_record_list.html',
                      {'all_consult_record': all_consult_record[page.data_start: page.data_end],
                       'all_tag': page.show_li})

    def post(self, request, customer_id):
        # 获取用户选择的操作
        action = request.POST.get('action')
        # 用反射查看这个操作是否可执行
        if getattr(self, action):
            # 执行这个操作
            getattr(self, action)()

        return self.get(request, customer_id)

    # 删除用户
    def delete(self):
        ids = self.request.POST.getlist('id')
        models.ConsultRecord.objects.filter(id__in=ids).delete()


# 添加修改咨询记录二合一
def consult_record_add_or_edit(request, edit_id=None):
    cr_obj = models.ConsultRecord.objects.filter(id=edit_id).first() or models.ConsultRecord(consultant=request.user)
    form_obj = ConsultRecordForm(instance=cr_obj)

    if request.method == 'POST':
        form_obj = ConsultRecordForm(request.POST, instance=cr_obj)

        if form_obj.is_valid():
            form_obj.save()

            return redirect(reverse('consult', args=('0',)))

    return render(request, 'crm/sales/consult_record_add_or_edit.html', {'form_obj': form_obj, 'edit_id': edit_id})


# 报名记录列表
class EnrollmentList(View):

    def get(self, request, customer_id):
        # 获取记录
        if customer_id == '0':
            all_record = models.Enrollment.objects.filter(customer__consultant=request.user, delete_status=False)
        else:
            all_record = models.Enrollment.objects.filter(customer_id=customer_id, customer__consultant=request.user,
                                                          delete_status=False)

        query_params = request.GET.copy()
        # 分页功能
        page = Pagination(request, len(all_record), query_params, each_page_data=10)

        return render(request, 'crm/sales/enrollment_list.html',
                      {'all_record': all_record[page.data_start: page.data_end],
                       'all_tag': page.show_li})

    def post(self, request, customer_id):
        # 获取用户选择的操作
        action = request.POST.get('action')
        # 用反射查看这个操作是否可执行
        if getattr(self, action):
            # 执行这个操作
            getattr(self, action)()

        return self.get(request, customer_id)

    # 删除用户
    def delete(self):
        ids = self.request.POST.getlist('id')
        models.Enrollment.objects.filter(id__in=ids).delete()


# 添加或编辑报名记录
def enrollment_add_or_edit(request, customer_id=None, edit_id=None):
    enrollment_obj = models.Enrollment.objects.filter(id=edit_id).first() or models.Enrollment(customer_id=customer_id)
    form_obj = EnrollmentForm(instance=enrollment_obj)

    if request.method == 'POST':
        form_obj = EnrollmentForm(request.POST, instance=enrollment_obj)
        # 如果客户同意协议内容, 则进行校验, 否则取消提交
        if request.POST.get('contract_agreed') == 'on':
            if form_obj.is_valid():
                # 保存报名记录
                obj = form_obj.save()
                # 将这个客户的状态改为已报名
                obj.customer.status = 'signed'
                obj.customer.save()

                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect(reverse('enrollment', args=('0',)))

    return render(request, 'crm/sales/enrollment_add_or_edit.html', {'form_obj': form_obj, 'next': request.GET.get('next')})
