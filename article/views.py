from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
# 导入数据模型ArticlePost
from . import models
from .models import ArticlePost
# 引入User模型
from django.contrib.auth.models import User
# 引入分页模块
from django.core.paginator import Paginator


def article_list(request):
    # 根据GET请求中查询条件
    # 返回不同排序的对象数组
    if request.GET.get('order') == 'total_views':
        article_list = ArticlePost.objects.all().order_by('-total_views')
        order = 'total_views'
    else:
        article_list = ArticlePost.objects.all()
        order = 'normal'

    paginator = Paginator(article_list, 4)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    # 修改此行
    context = {'articles': articles, 'order': order}

    return render(request, 'article/list.html', context)


def article_create(request):
    if request.method == 'POST':
        new_article_title = request.POST.get('title')
        new_article_body = request.POST.get('body')
        new_article_author = User.objects.get(id=1)
        models.ArticlePost.objects.create(
            title=new_article_title, body=new_article_body, author=new_article_author)
        return redirect("article:article_list")
    # 如果用户请求获取数据
    else:
        return render(request, 'article/create.html')

# 文章详情


def article_detail(request, id):
    # 取出相应的文章
    article = ArticlePost.objects.get(id=id)
    # 浏览量 +1
    article.total_views += 1
    article.save(update_fields=['total_views'])

    # 需要传递给模板的对象
    # context = { 'article': article }
    context = {'article': article}
    # 载入模板，并返回context对象
    return render(request, 'article/detail.html', context)

# 删文章


def article_delete(request, id):
    # 根据 id 获取需要删除的文章
    article = ArticlePost.objects.get(id=id)
    # 调用.delete()方法删除文章
    article.delete()
    # 完成删除后返回文章列表
    return redirect("article:article_list")

# 更新文章
# 提醒用户登录


@login_required(login_url='/user/login/')
def article_update(request, id):
    # # 获取需要修改的具体文章对象
    article = ArticlePost.objects.get(id=id)
    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")

    # 判断用户是否为 POST 提交表单数据
    if request.method == "POST":
        new_article_title = request.POST.get('title')
        new_article_body = request.POST.get('body')
        article.title = new_article_title
        article.body = new_article_body
        article.save()
        # 完成后返回到修改后的文章中。需传入文章的 id 值
        return redirect("article:article_detail", id=id)
    else:
        # 赋值上下文，将 article 文章对象也传递进去，以便提取旧的内容
        context = {'article': article}
        return render(request, 'article/update.html', context)
