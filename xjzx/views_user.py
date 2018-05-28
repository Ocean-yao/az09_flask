from flask import Blueprint,render_template, jsonify
from flask import current_app
from flask import make_response
from flask import request
from flask import session
import re
import random
from models import db,UserInfo
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
    print(dict1)
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
            avatar = '/static/news/images/' + user.avatar
            return jsonify(result=3, avatar=avatar, nick_name=user.nick_name)
        else:
            return jsonify(result=4)
    else:
        return jsonify(result=2)


@user_blueprint.route('/logout',methods=['POST'])
def logout():
    session.pop('user_id')
    return jsonify(result=1)