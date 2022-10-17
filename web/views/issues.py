import json

from django.core.paginator import Page, Paginator, PageNotAnInteger, InvalidPage, EmptyPage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from web import models
from web.utils import check_login
from web.forms.issues import IssuesModelForm


@check_login
def issues_home(request, project_id):
    try:
        project = models.Project.objects.get(id=project_id)
    except Exception:
        return redirect('project_list')

    if request.method == 'GET':
        # issues
        all_issues = models.Issues.objects.filter(project=project).order_by('id')
        # 生成分页
        paginator = Paginator(all_issues, 5)
        cur_page_idx = request.GET.get('page')

        try:
            issue_list = paginator.page(cur_page_idx)
            cur_page_idx = int(cur_page_idx)
        except PageNotAnInteger:
            # 如果请求的页数不是整数, 返回第一页。
            issue_list = paginator.page(1)
            cur_page_idx = 1
        except EmptyPage:
            # 如果请求的页数不在合法的页数范围内，返回结果的最后一页。
            issue_list = paginator.page(paginator.num_pages)
        except InvalidPage:
            return redirect('issues')

        # 生成页码
        if cur_page_idx < 6:
            if paginator.num_pages <= 10:
                page_range = range(1, paginator.num_pages + 1)
            else:
                page_range = range(1, 11)
        elif (cur_page_idx >= 6) and (cur_page_idx <= paginator.num_pages - 5):
            page_range = range(cur_page_idx - 5, cur_page_idx + 5)
        else:
            page_range = range(paginator.num_pages - 9, paginator.num_pages + 1)

        have_next = cur_page_idx < paginator.num_pages
        if have_next:
            next_page_idx = cur_page_idx + 1
        have_prev = cur_page_idx != 1
        if have_prev:
            prev_page_idx = cur_page_idx - 1

        form = IssuesModelForm(project=project, method='GET')
        return render(request, 'web/issue_home.html', locals())


@check_login
def issue_detail(request, project_id, issue_id):
    try:
        project = models.Project.objects.get(id=project_id)
        issue = models.Issues.objects.get(id=issue_id)  # 查询当前issue的内容
    except Exception:
        return redirect('project_list')

    if request.method == 'GET':
        form = IssuesModelForm(instance=issue, project=project, method='GET')
        return render(request, 'web/issue_detail.html', locals())
    elif request.method == 'POST':
        # 编辑
        form = IssuesModelForm(instance=issue, project=project, method='POST', data=request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': True})
        else:
            return JsonResponse({'status': False, 'error': form.errors})


@check_login
def issue_from_check(request, project_id):
    try:
        project = models.Project.objects.get(id=project_id)
    except Exception:
        return redirect('project_list')
    if request.method == 'POST':
        form = IssuesModelForm(project=project, method='POST', data=request.POST)
        if form.is_valid():
            form.instance.project = project
            form.instance.creator = request.tracer.user
            form.save()
            return JsonResponse({'status': True})
        else:
            return JsonResponse({'status': False, 'error': form.errors})


@check_login
def issue_record(request, project_id, issue_id):
    try:
        project = models.Project.objects.get(id=project_id)
        issue = models.Issues.objects.get(id=issue_id, project_id=project_id)  # 查询当前issue
    except Exception:
        return redirect('project_list')
    # 获取当前issue的所有评论
    if request.method == 'GET':
        replies = issue.issuereply_set.all()
        data_list = []
        for row in replies:
            data = {
                'parent_id': row.parent_issue_reply_id,
                'id': row.id,
                'reply_type_text': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.username,
                'datetime': row.create_datetime.strftime('%Y-%m-%d %H:%M')
            }
            data_list.append(data)
        return JsonResponse({'status': True, 'data': data_list})
