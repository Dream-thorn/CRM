from django.conf.urls import url
from crm import views

urlpatterns = [
    # 客户列表
    url(r'^customer_list/', views.customer_list, name='customer'),
]
