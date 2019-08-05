from django.db import transaction
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import QueryDict
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import auth
from django.urls import reverse
from crm.forms import ClassForm, CourseForm, StudyRecordForm
from crm import models
from utils.pagination import Pagination
from django.views import View
from django.conf import settings


# 班级列表
class ClassList(View):

    def get(self, request):
        # 要查询的字段
        query_list = ['course', 'semester', 'price', 'start_date']
        q = self.get_search_content(query_list)
        # 如果要访问班级列表
        if request.path_info == reverse('class'):
            # 全部班级
            all_class = models.ClassList.objects.filter(q, )
        else:
            # 我的班级
            all_class = models.ClassList.objects.filter(q, teachers=request.user)

        query_params = request.GET.copy()  # QueryDict的深拷贝方法

        # 分页功能
        page = Pagination(request, len(all_class), query_params, each_page_data=10)

        # 下一个要跳转的url地址
        next_url = self.get_next().urlencode()  # next=%2Fcrm%2Fcustomer_list%2F%3Fquery%3Duser%26page%3D2

        return render(request, 'crm/teacher/class_list.html',
                      {'all_class': all_class[page.data_start: page.data_end],
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

    # 删除用户
    def delete(self):
        ids = self.request.POST.getlist('id')
        models.ClassList.objects.filter(id__in=ids).delete()

    # 模糊查询
    def get_search_content(self, query_list):
        query = self.request.GET.get('query', '')
        q = Q()
        q.connector = 'OR'
        for i in query_list:
            q.children.append(Q((f'{i}__contains', query)))

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


def class_add_or_edit(request, edit_id=None):
    edit_obj = models.ClassList.objects.filter(id=edit_id).first()
    form_obj = ClassForm(instance=edit_obj)

    if request.method == 'POST':
        form_obj = ClassForm(request.POST, instance=edit_obj)
        if form_obj.is_valid():
            form_obj.save()

            # 获取要跳转的地址
            next_url = request.GET.get('next')
            if next_url:
                # 跳转到这个地址
                return redirect(next_url)

            return redirect(reverse('class'))

    title = '编辑班级' if edit_id else '添加班级'

    return render(request, 'crm/teacher/add_or_edit.html',
                  {'form_obj': form_obj,
                   'edit_id': edit_id,
                   'user': request.user,
                   'title': title,
                   'next_url': reverse('my_class')})


# 课程列表
class CourseList(View):

    def get(self, request, class_id):
        # 要查询的字段
        query_list = ['day_num', 'course_title']
        q = self.get_search_content(query_list)

        if class_id == '0':
            all_course = models.CourseRecord.objects.filter(q, )
        else:
            all_course = models.CourseRecord.objects.filter(q, re_class_id=class_id)
        query_params = request.GET.copy()  # QueryDict的深拷贝方法

        # 分页功能
        page = Pagination(request, len(all_course), query_params, each_page_data=10)

        # 下一个要跳转的url地址
        next_url = self.get_next().urlencode()

        return render(request, 'crm/teacher/course_list.html',
                      {'all_course': all_course[page.data_start: page.data_end],
                       'all_tag': page.show_li,
                       'user': request.user,
                       'next': next_url})

    def post(self, request, class_id):
        # 获取用户选择的操作
        action = request.POST.get('action')
        # 用反射查看这个操作是否可执行
        if getattr(self, action):
            # 执行这个操作
            ret = getattr(self, action)()

            if ret:
                return ret

        return self.get(request, class_id)

    # 删除用户
    def delete(self):
        ids = self.request.POST.getlist('id')
        models.CourseRecord.objects.filter(id__in=ids).delete()

    # 根据当前提交的课程记录Id批量初识化学生的学习记录
    def init_study_record(self):
        # 获取要初始化学习记录的课程ID
        ids = self.request.POST.getlist('id')
        # 获取要初始化学习记录的课程对象
        course_obj_list = models.CourseRecord.objects.filter(id__in=ids)

        for course_obj in course_obj_list:
            # 查找每个课程对应的班级中的学生, 且状态为学习中
            student_list = course_obj.re_class.customer_set.filter(status='studying')

            # 要生成的学习记录
            study_record_list = []

            for student in student_list:
                # # 方案一
                # models.StudyRecord.objects.create(course_record=course_obj, student=student)
                # # 方案二
                # study_record_obj = models.StudyRecord(course_record=course_obj, student=student)
                # study_record_obj.save()
                # 方案三
                study_record_list.append(models.StudyRecord(course_record=course_obj, student=student))

            # 批量生成, 这样就只执行一次sql语句, 提高效率
            models.StudyRecord.objects.bulk_create(study_record_list)

    # 模糊查询
    def get_search_content(self, query_list):
        query = self.request.GET.get('query', '')
        q = Q()
        q.connector = 'OR'
        for i in query_list:
            q.children.append(Q((f'{i}__contains', query)))

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


def course_add_or_edit(request, class_id=None, edit_id=None):
    edit_obj = models.CourseRecord.objects.filter(id=edit_id).first() or models.CourseRecord(re_class_id=class_id,
                                                                                             teacher=request.user)
    form_obj = CourseForm(instance=edit_obj)

    if request.method == 'POST':
        form_obj = CourseForm(request.POST, instance=edit_obj)
        if form_obj.is_valid():
            form_obj.save()

            # 获取要跳转的地址
            next_url = request.GET.get('next')
            if next_url:
                # 跳转到这个地址
                return redirect(next_url)

            return redirect(reverse('course', args=('0',)))

    title = '编辑课程' if edit_id else '添加课程'

    return render(request, 'crm/teacher/add_or_edit.html',
                  {'form_obj': form_obj,
                   'edit_id': edit_id,
                   'user': request.user,
                   'title': title,
                   'next_url': reverse('course', args=('0',))})


# 学习记录
def study_record_list(request, course_id):
    # form集合
    FormSet = modelformset_factory(models.StudyRecord, StudyRecordForm, extra=0)
    queryset = models.StudyRecord.objects.filter(course_record_id=course_id)
    form_set = FormSet(queryset=queryset)

    if request.method == 'POST':
        form_set = FormSet(request.POST)
        if form_set.is_valid():
            form_set.save()

            return redirect(reverse('course', args=('0',)))

    return render(request, 'crm/teacher/study_record_list.html', {'form_set': form_set})
