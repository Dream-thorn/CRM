from django.conf.urls import url
from crm import views

urlpatterns = [
    # 客户列表
    url(r'^customer_list/', views.customer_list, name='customer'),
    # 添加客户
    url(r'^customer/add/', views.customer_add_or_edit, name='customer_add'),
    # 编辑客户
    url(r'^customer/edit/(\d+)/', views.customer_add_or_edit, name='customer_edit'),
]
