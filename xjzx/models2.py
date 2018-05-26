from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

import pymysql
pymysql.install_as_MySQLdb()

db = SQLAlchemy()

# 不继承db.Model,如果继承就会创建表，直接继承object
class BaseModel(object):
    create_time = db.Column(db.DateTime, default=datetime.now())
    update_time = db.Column(db.DateTime, default=datetime.now())
    isDelete = db.Column(db.Boolean, default=False)

tb_news_collect = db.Table(
    'tb_news_collect',
    db.Column('user_id', db.Integer, db.ForeignKey('user_info.id'), primary_key=True),
    db.Column('news_id', db.Integer, db.ForeignKey('news_info.id'), primary_key=True)
)
tb_user_follow = db.Table(
    'tb_user_follow',
    db.Column('origin_user_id', db.Integer, db.ForeignKey('user_info.id'), primary_key=True),
    db.Column('follow_user_id', db.Integer, db.ForeignKey('user_info.id'), primary_key=True)
)

class NewsCategory(db.Model, BaseModel):
    __tablename__ = 'news_category'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    # 连接表的news，参数一指的是类名，返回一个对方连接我，
    news = db.relationship('NewsInfo', backref='category', lazy='dynamic')

class NewsInfo(db.Model,BaseModel):
    __tablename__='news_info'

    id = db.Column(db.Integer, primary_key=True)
    # 首页的图片
    pic = db.Column(db.String(50))
    # 首页标题
    title = db.Column(db.String(30))
    # detail摘要
    summary = db.Column(db.String(200))
    # detail内容
    content = db.Column(db.Text)
    # 点击排名
    click_count = db.Column(db.Integer,default=0)
    # 新闻列表审核状态
    status = db.Column(db.SmallInteger,default=1)
    # 新闻列表审核未通过的原因
    reason = db.Column(db.String(100),default='')

    # 新闻来源，由于没有按键可以提交，所以取消
    # source = db.Column(db.String(20), default='')

    # 发布者
    user_id = db.Column(db.Integer)
    # 新闻分类，后面的是foreign的参数使用的是表名
    category_id = db.Column(db.Integer, db.ForeignKey('news_category.id'))

    # detail里面有评论的数量
    comment_count = db.Column(db.Integer,default=0)
    comments = db.relationship()


class UserInfo(db.Model,BaseModel):
    __tablename__ = 'user_info'

    id = db.Column(db.Integer, primary_key=True)
    # 头像，不是很明白这个default的东西是什么
    avatar = db.Column(db.String(50), default='user_pic.png')
    nick_name = db.Column(db.String(20))
    signature = db.Column(db.String(200))
    # 发布的新闻数量，忘记设置默认值
    public_count = db.Column(db.Integer, default=0)
    # 粉丝数量
    follow_count = db.Column(db.Integer, default=0)
    mobile = db.Column(db.String(11))
    password_hash = db.Column(db.String(200))
    gender = db.Column(db.Boolean, default=False)
    isAdmin = db.Column(db.Boolean, default=False)

    news = db.relationship('NewsInfo', backref='user', lazy='dynamic')

    news_collect = db.relationship(
        'NewsInfo',
        secondary=tb_news_collect,
        lazy='dynamic'
    )

    follow_user = db.relationship(
        'UserInfo',
        secondary=tb_user_follow,
        lazy='dynamic',
        primaryjoin=id == tb_user_follow.c.origin_user_id,
        secondaryjoin=id == tb_user_follow.c.follow_user_id,
        backref=db.backref('follow_by_user', lazy='dynamic')
    )



class NewsComment(db.Model, BaseModel):
    __tablename__ = 'news_comment'
    id = db.Column(db.Integer,primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news_info.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'))
    like_count = db.Column(db.Integer, default=0)
    content = db.Column(db.String())
    msg = db.Column(db.String(200))

    comment_id = db.Column(db.Integer, db.ForeignKey('news_comment.id'))
    comments = db.relationship('NewsComment', lazy='dynamic')



