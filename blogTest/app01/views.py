from django.shortcuts import render,redirect,HttpResponse
from utils.code import check_code

# Create your views here.
from django.db.models import Count,Avg,Max
from django.contrib import auth
from app01.models import Article,UserInfo,Category,Tag,Article2Tag

# def get_query_data(username):
#     user = UserInfo.objects.filter(username=username).first()
#     blog = user.blog
#     # 查询当前站点每一个分类的名称及对应的文章数
#     cate_list = Category.objects.filter(blog=blog).annotate(c=Count('article__title')).values_list('title', 'c')
#     # 查询当前站点每一个标签的名称及对应的文章数
#     tag_list = Tag.objects.filter(blog=blog).annotate(c=Count('article__title')).values_list('title', 'c')
#     # 日期归档
#     date_list = Article.objects.filter(user=user).extra(
#         select={"y_m_date": "DATE_FORMAT(create_time,'%%Y-%%m')"}).values('y_m_date').annotate(
#         c=Count('title')).values_list('y_m_date', 'c')
#     return {'blog':blog,'username':username,'cate_list':cate_list,'tag_list':tag_list,'date_list':date_list}

def code(request):
    img,random_code = check_code()
    request.session['random_code'] = random_code
    from io import BytesIO
    stream = BytesIO()
    img.save(stream,'png')
    return HttpResponse(stream.getvalue())


def login(request):
    if request.method=='POST':
        print('++++++++',request.POST) # <QueryDict: {'csrfmiddlewaretoken': ['9WcnULgXwbMWAVQL9j6Tr2pxDb0amG0Mg295BEYJnvt4Yczb9o6WLOVJaBEAE6U0'], 'pwd': ['alex1234'], 'user': ['alex']}>
        user=request.POST.get('user')
        pwd=request.POST.get('pwd')
        code=request.POST.get('code')
        if code.upper() != request.session['random_code'].upper():
            return render(request,'login.html',{'msg':'验证码错误'})
        user=auth.authenticate(username=user,password=pwd)
        if user:
            auth.login(request,user)
            return redirect('/index/')
    return render(request,'login.html')

def index(request):
    article_list=Article.objects.all()
    return render(request,'index.html',locals())

def logout(request):
    auth.logout(request)
    return redirect('/index/')

def homesite(request,username,**kwargs):
    user = UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request,'not_found.html')

    blog=user.blog
    print('909090888')
    # 查询当前站点每一个分类的名称及对应的文章数
    cate_list=Category.objects.filter(blog=blog).annotate(c=Count('article__title')).values_list('title','c')
    print(cate_list)
    # 查询当前站点每一个标签的名称及对应的文章数
    tag_list=Tag.objects.filter(blog=blog).annotate(c=Count('article__title')).values_list('title','c')
    # 日期归档
    date_list=Article.objects.filter(user=user).extra(select={"y_m_date":"DATE_FORMAT(create_time,'%%Y-%%m')"}).values('y_m_date').annotate(c=Count('title')).values_list('y_m_date','c')
    print(date_list)
    if not kwargs:
        article_list=Article.objects.filter(user_id=user.pk)
    else:
        condition=kwargs.get('condition')
        params=kwargs.get('params')
        if condition=='category':
            article_list=Article.objects.filter(user_id=user.pk).filter(category__title=params)
        elif condition=='tag':
            article_list=Article.objects.filter(user_id=user.pk).filter(tags__title=params)
        else:
            year,month=params.split('-')
            article_list=Article.objects.filter(user_id=user.pk).filter(create_time__year=year,create_time__month=month)
    return render(request,'homesite.html',locals())

def article_detail(request,username,article_id):
    print('1234567')
    user=UserInfo.objects.filter(username=username).first()
    blog=user.blog
    # 查询当前站点每一个分类的名称及对应的文章数
    cate_list = Category.objects.filter(blog=blog).annotate(c=Count('article__title')).values_list('title', 'c')
    # 查询当前站点每一个标签的名称及对应的文章数
    tag_list = Tag.objects.filter(blog=blog).annotate(c=Count('article__title')).values_list('title', 'c')
    # 日期归档
    date_list = Article.objects.filter(user=user).extra(
        select={"y_m_date": "DATE_FORMAT(create_time,'%%Y-%%m')"}).values('y_m_date').annotate(
        c=Count('title')).values_list('y_m_date', 'c')
    # con_text=get_query_data(username)
    # print('666666',con_text)
    article_obj = Article.objects.filter(pk=article_id).first()
    print('888888',locals())
    comment_list=Comment.objects.filter(article_id=article_id)
    return render(request,'article_datail.html',locals())

from app01.models import ArticleUpDown,Comment
import json
from django.http import JsonResponse
from django.db.models import F
from django.db import transaction
def digg(request):
    print(request.POST)
    is_up=json.loads(request.POST.get('is_up'))
    article_id=request.POST.get('article_id')
    user_id=request.user.pk
    response={"state":True,"msg":None}

    obj=ArticleUpDown.objects.filter(user_id=user_id,article_id=article_id).first()
    if obj:
        response["state"]=False
        response["handled"]=obj.is_up
    else:
        with transaction.atomic():
            new_obj=ArticleUpDown.objects.create(user_id=user_id,article_id=article_id,is_up=is_up)
            if is_up:
                Article.objects.filter(pk=article_id).update(up_count=F("up_count")+1)
            else:
                Article.objects.filter(pk=article_id).update(down_count=F("down_count")+1)
    return JsonResponse(response)

def comment(request):
    # 获取数据
    user_id=request.user.pk
    print('@@@@@@@@@@@@@',user_id)
    article_id=request.POST.get('article_id')
    pid=request.POST.get('pid')
    content=request.POST.get('content')
    # 生成评论对象
    with transaction.atomic():
        comment=Comment.objects.create(user_id=user_id,article_id=article_id,content=content,parent_comment_id=pid)
        Article.objects.filter(pk=article_id).update(comment_count=F('comment_count')+1)

    response={"state":True}
    response["timer"]=comment.create_time.strftime('%Y-%m-%d %X')
    response["content"]=comment.content
    response["user"]=request.user.username

    return JsonResponse(response)

def backend(request):
    user=request.user
    article_list=Article.objects.filter(user=user)
    return render(request,'backend/backend.html',locals())


def add_article(request):
    if request.method=='POST':
        title=request.POST.get('title')
        content=request.POST.get('content')
        user=request.user
        cate_pk=request.POST.get('cate')
        tag_pk_list=request.POST.getlist('tags')

        import bs4
        from bs4 import BeautifulSoup
        soup=BeautifulSoup(content,"html.parser")

        # 文章过滤
        for tag in soup.find_all():
            if tag.name in ["script",]:
                tag.decompose()   # 如果有script标签 就删除script标签  利用bs模块防止XSS攻击
        # 切片文章文本
        desc=soup.text[0:150]
        print('789789',desc)

        article_obj=Article.objects.create(title=title,content=str(soup),user=user,category_id=cate_pk,desc=desc)
        for tag_pk in tag_pk_list:
            Article2Tag.objects.create(article_id=article_obj.pk,tag_id=tag_pk)
        return redirect('/backend/')


    else:
        blog=request.user.blog
        cate_list=Category.objects.filter(blog=blog)
        tags=Tag.objects.filter(blog=blog)
        return render(request,'backend/add_article.html',locals())

from blogTest import settings
import os
def upload(request):
    print(request.FILES)
    obj=request.FILES.get('upload_img')
    name=obj.name

    # path = settings.BASE_DIR
    path = os.path.join(settings.BASE_DIR,'static','upload',name)   # 拼成一个文件的绝对路径
    with open(path,'wb') as f:
        for line in obj:
            f.write(line)
    import json
    res={
        "error":0,
        "url":"/static/upload/"+name
    }
    return HttpResponse(json.dumps(res))


