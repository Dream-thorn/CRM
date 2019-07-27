from django.utils.safestring import mark_safe


class Pagination:

    def __init__(self, request, all_data_len, each_page_data=10, max_page=11):
        """
        分页器
        :param request: request
        :param all_data_len: 全部数据的长度
        :param each_page_data: 每页要显示的数据数量
        :param max_page: 当前页面最大显示多少页码
        """

        self.each_page_data = each_page_data
        self.url = request.path_info

        """每页数据相关"""
        # 计算总页数
        self.total_page, more = divmod(all_data_len, self.each_page_data)
        if more:
            self.total_page += 1

        # 获取用户要访问的页码数
        try:
            self.page = int(request.GET.get('page', 1))
            if self.page <= 0:
                self.page = 1
            elif self.page > self.total_page:
                self.page = self.total_page
        except:
            self.page = 1

        """页码相关"""
        # 每页一半的页码数
        half_page = max_page // 2
        # 根据用户要访问的页码, 生成当前页面的开始和结束页码
        if self.total_page < max_page:  # 如果总页数小于每页页码的最大数量
            self.start_page = 1
            self.end_page = self.total_page
        else:
            if self.page - half_page <= 0:
                self.start_page = 1
                self.end_page = max_page
            elif self.page + half_page > self.total_page:
                self.start_page = self.total_page - half_page
                self.end_page = self.total_page
            else:
                self.start_page = self.page - half_page
                self.end_page = self.page + half_page

    # 获取对应页数数据的开始下标
    @property
    def data_start(self):
        return (self.page - 1) * self.each_page_data

    # 获取对应页数数据的结束下标
    @property
    def data_end(self):
        return self.page * self.each_page_data

    # 在后端生成li标签
    @property
    def show_li(self):
        # 全部要显示的标签
        tag_list = []

        # 首页标签
        first_tag = f'<li><a href="{self.url}?page=1">首页&nbsp;</a></li>'
        tag_list.append(first_tag)

        if self.page == 1:
            tag = f'<li class="disabled"><a">&laquo;&nbsp;</a></li>'
        else:
            tag = f'<li><a href="{self.url}?page={self.page - 1}">&laquo;&nbsp;</a></li>'
        tag_list.append(tag)

        for num in range(self.start_page, self.end_page + 1):
            tag = f'<li><a href="{self.url}?page={num}">{num}&nbsp;</a></li>'
            tag_list.append(tag)

        if self.page == self.total_page:
            tag = f'<li class="disabled"><a">&raquo;&nbsp;</a></li>'
        else:
            tag = f'<li><a href="{self.url}?page={self.page + 1}">&raquo;&nbsp;</a></li>'
        tag_list.append(tag)

        # 尾页标签
        last_tag = f'<li><a href="{self.url}?page={self.total_page}">尾页</a></li>'
        tag_list.append(last_tag)

        # 让这些标签能在前端直接使用
        return mark_safe(''.join(tag_list))
