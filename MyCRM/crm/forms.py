from django import forms
from django.core.exceptions import ValidationError

from crm import models


# 注册form
class RegForm(forms.ModelForm):
    username = forms.CharField(
        label='用户名',
        widget=forms.widgets.EmailInput(),
        max_length=12,
        error_messages={
            'required': '不能为空',
        }
    )
    password = forms.CharField(
        label='密码',
        widget=forms.widgets.PasswordInput(),
        min_length=6,
        max_length=24,
        error_messages={
            'min_length': '最小长度为6',
            'required': '不能为空'
        }
    )
    re_password = forms.CharField(
        label='确认密码',
        widget=forms.widgets.PasswordInput(),
        min_length=6,
        max_length=24,
        error_messages={
            'min_length': '最小长度为6',
            'required': '不能为空'
        }
    )
    name = forms.CharField(
        label='姓名',
        widget=forms.widgets.Input(),
        min_length=1,
        max_length=12,
        error_messages={
            'min_length': '最小长度为1',
            'required': '不能为空'
        }
    )

    class Meta:
        model = models.UserProfile
        # fields = '__all__'    # 所有字段
        fields = ['username', 'password', 're_password', 'name', 'department']
        # exclude = []    # 要排除的字段
        widgets = {
            'password': forms.widgets.PasswordInput()
        }
        labels = {
            'department': '部门',
        }

    def __init__(self, *args, **kwargs):
        super(RegForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    # 全局钩子
    def clean(self):
        pwd = self.cleaned_data.get('password')
        re_pwd = self.cleaned_data.get('re_password')
        if re_pwd == pwd:
            return self.cleaned_data

        self.add_error('re_password', '两次密码不一致')
        raise ValidationError('两次密码不一致')
