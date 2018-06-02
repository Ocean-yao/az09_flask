import functools

from flask import Blueprint,render_template, jsonify
from flask import current_app
from flask import make_response
from flask import redirect
from flask import request
from flask import session
import re
import random
from models import db,UserInfo,NewsInfo,NewsCategory
from datetime import datetime
# from utils.ytx_sdk import ytx_send

user_blueprint = Blueprint('user',__name__,url_prefix='/user')


# 写出图像识别的视图
@user_blueprint.route('/image_yzm')
def image_yzm():
    from utils.captcha.captcha import captcha

    #返回三个值，第一个是自己随机生成的字符串，验证码，图片的二进制数据
    name, yzm, buffer = captcha.generate_captcha()

    #使用session保存数据
    session['image_yzm'] = yzm

    #生成响应
    response = make_response(buffer)

    #默认返回的内容会被当做text/html解析，如下代码告诉浏览器解释为图片
    response.mimetype = 'image/png'
    return response


@user_blueprint.route('/sms_yzm')
def sms_yzm():
    # 得到对方提交的数据
    dict1 = request.args
    print(dict1)
    mobile = dict1.get('mobile')
    image_yzm = dict1.get('image_yzm')
    if image_yzm != session.get('image_yzm'):
        return jsonify(result=1)

    #前段点击获取验证码，并将电话号码和图片的验证码发送过来，在传回验证码之前，对图片验证码进行判断

    #随机生成一个数字（4位）
    yzm = random.randint(1000,9999)
    #保存到session
    session['sms_yzm'] = yzm
    print('image_yzm is %s' % yzm)

    # ytx_send.sendTemplateSMS(mobile,{yzm,5},1)
    print(yzm)
    return jsonify(result=2)


@user_blueprint.route('/register',methods=['POST'])
def register():
    # 收取数据
    dict1 = request.form
    # print('点击注册传过来的参数：%s' % dict1)
    mobile = dict1.get('mobile')
    image_yzm = dict1.get('image_yzm')
    sms_yzm = dict1.get('sms_yzm')
    pwd = dict1.get('pwd')
    # csrf_token = dict1.get('csrf_token')

    # 判断所有数据是否存在
    if not all([mobile, image_yzm, sms_yzm, pwd]):
        return jsonify(result=1)

    # 判断手机号是否存在，需要到数据库拿数据
    mobile_count = UserInfo.query.filter_by(mobile=mobile).count()
    if mobile_count>0:
        return jsonify(result=2)

    # 判断图片是否正确
    if image_yzm != session.get('image_yzm'):
        return jsonify(result=3)

    # 判断短信是否正确,接收到的数据是字符串，需要转为int类型
    if int(sms_yzm) != session.get('sms_yzm'):
        return jsonify(result=4)

    # 判断密码是否正确
    if not re.match(r'[a-zA-Z0-9_]{6,20}',pwd):
        return jsonify(result=5)

    # 创建对象
    user = UserInfo()
    user.nick_name = mobile
    user.mobile = mobile
    user.password = pwd

    # 保存提交
    try:
        db.session.add(user)
        db.session.commit()
    except:
        current_app.logger_xjzx.error('注册用户时数据库访问失败')
        return jsonify(result=6)

    return jsonify(result=7)


@user_blueprint.route('/login')
def login():
    # 获取数据
    dict1 = request.args
    mobile = dict1.get('mobile')
    password = dict1.get('pwd')

    # 需要先判断是否为空
    if not all([mobile,password]):
        return jsonify(result=1)

    # 生成对象的方式相当于执行了一句sql语句，如果没有找到对应的对象，返回空
    user = UserInfo.query.filter_by(mobile=mobile).first()

    if user:
        # 需要判断密码是否正确
        if user.check_pwd(password):
            # 登陆成功，状态保持
            session['user_id'] = user.id
            avatar = user.avatar_url
            return jsonify(result=3, avatar=avatar, nick_name=user.nick_name)
        else:
            return jsonify(result=4)
    else:
        return jsonify(result=2)


@user_blueprint.route('/logout',methods=['POST'])
def logout():

    session.pop('user_id')
    return jsonify(result=1)


@user_blueprint.route('/show')
def show():
    if 'user_id' in session:
        return 'ok'
    else:
        return 'no'


def login_required(f):
    @functools.wraps(f)  # 返回f函数的名称，而不是用fun2代替这个函数的名称
    def fun2(*args, **kwargs):
        # 可以写成'user_id is in session',如果使用get，没有值则返回none
        if session.get('user_id'):
            return f(*args, **kwargs)
        else:
            return redirect('/')
    return fun2


@user_blueprint.route('/')
@login_required #相当于index= fun1（index）
def index():
    title = '用户中心'
    user_id = session['user_id']
    # 忘记写first()了
    # user = UserInfo.query.get(user_id)
    user = UserInfo.query.filter_by(id=user_id).first()
    return render_template('/news/user.html', title=title, user=user)


@user_blueprint.route('/base',methods=['POST','GET'])
@login_required
def base():
    user_id = session['user_id']
    user = UserInfo.query.get(user_id)

    if request.method=='GET':
        return render_template('/news/user_base_info.html',user=user)

    elif request.method=='POST':
        # 错了两处，一个是gender转为布尔值，漏写异常捕获，还有日志
        dict1 = request.form
        signature = dict1.get('signature')
        nick_name = dict1.get('nick_name')
        gender = dict1.get('gender')
        if gender=='1':
            gender = True
        elif gender=='0':
            gender = False

        user.signature = signature
        user.nick_name = nick_name
        user.gender = gender
        print(user.gender)

        try:
            db.session.commit()
        except:
            current_app.logger_xjzx.error('连接数据库出错')
            return jsonify(result=2)

        return jsonify(result=1)


@user_blueprint.route('/pic', methods=['GET','POST'])
@login_required
def pic():
    user_id = session['user_id']
    user = UserInfo.query.get(user_id)
    if request.method=='GET':
        return render_template('news/user_pic_info.html', user=user)
    elif request.method=='POST':
        # 将数据保存在七牛云
        f1 = request.files.get('avatar')
        from utils.qiniu_xjzx import upload_pic
        f1_name = upload_pic(f1)
        user.avatar = f1_name
        db.session.commit()
        return jsonify(result=1, avatar_url=user.avatar_url)


@user_blueprint.route('/follow')
@login_required
def follow():
    # 获取数据
    user_id = session['user_id']
    user = UserInfo.query.get(user_id)

    # 对数据进行分页处理
    # 获取当前数据，前端将页数作为参数传过来
    page = int(request.args.get('page','1'))
    pagination = user.follow_user.paginate(page, 4, False)
    user_list = pagination.items
    total_page = pagination.pages
    return render_template('news/user_follow.html',
                           user_list=user_list,
                           total_page=total_page,
                           page=page)


@user_blueprint.route('/pwd', methods=['POST', 'GET'])
@login_required
def pwd():
    user_id = session['user_id']
    user = UserInfo.query.get(user_id)
    if request.method == 'GET':
        return render_template('news/user_pass_info.html')
    elif request.method == 'POST':
        # 收取post请求中带的参数
        dict1 = request.form
        print(dict1)
        current_pwd = dict1.get('current_pwd')
        print(current_pwd)
        new_pwd = dict1.get('new_pwd')
        print(new_pwd)
        new_pwd2 = dict1.get('new_pwd2')
        print(new_pwd2)

        # 对获取的数据进行判断
        # 你居然在变量上加上‘’......
        if not all([current_pwd, new_pwd, new_pwd2]):
            return render_template('news/user_pass_info.html', msg='不能为空！')

        elif not re.match(r'[a-zA-Z0-9_]{6,20}', current_pwd):

            return render_template('news/user_pass_info.html', msg='密码错误')

        elif not re.match(r'[a-zA-Z0-9_]{6,20}',new_pwd):
            return render_template(
                'news/user_pass_info.html',
                msg='新密码格式错误（长度为6-20，内容为大小写a-z字母，0-9数字，下划线_）'
            )

        elif new_pwd != new_pwd2:
            msg = '修改的密码不相等！'
            return render_template('news/user_pass_info.html', msg='修改的密码不相等！')

        elif not user.check_pwd(current_pwd):
            return render_template('news/user_pass_info.html', msg='当前密码输入错误！')

        else:
            user.password = new_pwd
            db.session.commit()
            return render_template('news/user_pass_info.html', msg='完成密码修改！')


@user_blueprint.route('/collect')
@login_required
def collect():
    user_id = session['user_id']
    user = UserInfo.query.get(user_id)

    # 数据分页处理
    # 获取页数参数，有前端提供
    page = int(request.args.get('page',1))
    pagination = user.news_collect.order_by(NewsInfo.id.desc()).paginate(page, 6, False)
    news_list = pagination.items
    total_page = pagination.pages
    return render_template('news/user_collection.html',
                           page=page,
                           news_list=news_list,
                           total_page=total_page)


@user_blueprint.route('/release', methods=['POST','GET'])
@login_required
def release():
    user_id = session['user_id']
    news_id = request.args.get('news_id')
    catagory_list = NewsCategory.query.all()

    if request.method == 'GET':

        if news_id == None:
            return render_template('news/user_news_release.html', catagory_list=catagory_list, news=None)
        else:
            news = NewsInfo.query.get(int(news_id))
            return render_template('news/user_news_release.html', catagory_list=catagory_list, news=news)

    elif request.method == 'POST':
        # 获取数据
        dict1 = request.form
        title = dict1.get('title')
        category_id = dict1.get('category')
        summary = dict1.get('summary')
        content = dict1.get('content')
        # 接受图片
        news_pic = request.files.get('news_pic')

        #  判断条件(如果是通过news的名字进入release页面，已经显示了图片，可以不用对图片进行判断)
        if news_id is None:
            if not all([title, category_id, summary, content, news_pic]):
                return render_template('news/user_news_release.html', msg='请将数据填写完整！', news=None)
        else:
            if not all([title, category_id, summary, content]):
                news = NewsInfo.query.get(int(news_id))
                return render_template('news/user_news_release.html', msg='请将数据填写完整！', news=news)

        # 获取上传的图片，并获取文件的名字,这里不能以news_id进行判断，因为原文件也可能出现更改图片的情况
        if news_pic:
            from utils.qiniu_xjzx import upload_pic
            filename = upload_pic(news_pic)
        else:
            news = NewsInfo.query.get(int(news_id))
            filename = news.pic

        # 创建news对象
        if news_id is None:
            news = NewsInfo()
        else:
            # 使用字符串进行查找，不要转换为int
            news = NewsInfo.query.get(news_id)

        # 对news对象的属性进行赋值
        news.title = title
        news.summary = summary
        news.content = content
        news.user_id = user_id
        news.pic = filename
        news.category_id = int(category_id)
        news.status = 1
        news.update_time = datetime.now()
        print(datetime.now())

        # 添加上传对象
        db.session.add(news)
        db.session.commit()

        # 这里是转向，不是render_template跳转到网页
        return redirect('/user/newslist')


@user_blueprint.route('/newslist')
@login_required
def newslist():
    user_id = session['user_id']
    user = UserInfo.query.get(user_id)
    # 数据分页
    page = int(request.args.get('page', 1))
    pagination = user.news.order_by(NewsInfo.update_time.desc()).paginate(page, 6, False)
    news_list = pagination.items
    total_page = pagination.pages
    return render_template('news/user_news_list.html',
                           page=page,
                           news_list=news_list,
                           total_page=total_page)

