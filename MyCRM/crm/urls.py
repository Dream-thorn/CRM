from django.conf.urls import url
from crm import views

urlpatterns = [
    # # 公有客户列表
    # url(r'^customer_list/', views.customer_list, name='customer'),
    # # 私有客户
    # url(r'^my_customer_list/', views.customer_list, name='my_customer'),

    # 公有客户列表
    url(r'^customer_list/', views.CustomerList.as_view(), name='customer'),
    # 私有客户
    url(r'^my_customer_list/', views.CustomerList.as_view(), name='my_customer'),
    # 添加客户
    url(r'^customer/add/', views.customer_add_or_edit, name='customer_add'),
    # 编辑客户
    url(r'^customer/edit/(\d+)/', views.customer_add_or_edit, name='customer_edit'),

    # 全部咨询记录
    url(r'^consult_record_list/(\d+)/', views.ConsultRecordList.as_view(), name='consult'),
    # 添加咨询记录
    url(r'^consult_record/add/', views.consult_record_add_or_edit, name='consult_record_add'),
    # 编辑咨询记录
    url(r'^consult_record/edit/(\d+)/', views.consult_record_add_or_edit, name='consult_record_edit'),

    # 全部报名记录
    url(r'^enrollment_list/(\d+)/', views.EnrollmentList.as_view(), name='enrollment'),
    # 添加报名记录
    url(r'^enrollment/add/(?P<customer_id>\d+)/', views.enrollment_add_or_edit, name='enrollment_add'),
    # 编辑报名记录
    url(r'^enrollment/edit/(?P<edit_id>\d+)/', views.enrollment_add_or_edit, name='enrollment_edit'),

]
