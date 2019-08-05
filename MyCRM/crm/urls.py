from django.conf.urls import url
from crm.views import sales, teacher

urlpatterns = [

    ### 销售相关 ###
    # 公有客户列表
    url(r'^customer_list/', sales.CustomerList.as_view(), name='customer'),
    # 私有客户
    url(r'^my_customer_list/', sales.CustomerList.as_view(), name='my_customer'),
    # 添加客户
    url(r'^customer/add/', sales.customer_add_or_edit, name='customer_add'),
    # 编辑客户
    url(r'^customer/edit/(\d+)/', sales.customer_add_or_edit, name='customer_edit'),

    # 全部咨询记录
    url(r'^consult_record_list/(\d+)/', sales.ConsultRecordList.as_view(), name='consult'),
    # 添加咨询记录
    url(r'^consult_record/add/', sales.consult_record_add_or_edit, name='consult_record_add'),
    # 编辑咨询记录
    url(r'^consult_record/edit/(\d+)/', sales.consult_record_add_or_edit, name='consult_record_edit'),

    # 全部报名记录
    url(r'^enrollment_list/(\d+)/', sales.EnrollmentList.as_view(), name='enrollment'),
    # 添加报名记录
    url(r'^enrollment/add/(?P<customer_id>\d+)/', sales.enrollment_add_or_edit, name='enrollment_add'),
    # 编辑报名记录
    url(r'^enrollment/edit/(?P<edit_id>\d+)/', sales.enrollment_add_or_edit, name='enrollment_edit'),


    ### 教师相关 ###
    # 班级列表
    url(r'^class_list/', teacher.ClassList.as_view(), name='class'),
    # 我的班级
    url(r'^my_class_list/', teacher.ClassList.as_view(), name='my_class'),
    # 添加班级
    url(r'^class/add/', teacher.class_add_or_edit, name='class_add'),
    # 编辑班级
    url(r'^class/edit/(\d+)/', teacher.class_add_or_edit, name='class_edit'),

    # 课程列表
    url(r'^course_list/(\d+)/', teacher.CourseList.as_view(), name='course'),
    # 添加课程
    url(r'^course/add/(?P<class_id>\d+)/', teacher.course_add_or_edit, name='course_add'),
    # # 编辑课程
    url(r'^course/edit/(?P<edit_id>\d+)/', teacher.course_add_or_edit, name='course_edit'),

    # 学习记录
    url(r'^study_record_list/(\d+)/', teacher.study_record_list, name='study_record'),

]
