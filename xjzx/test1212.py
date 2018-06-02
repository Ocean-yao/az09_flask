from flask import Blueprint,render_template, jsonify
from flask import request
from flask import session

from models import db,NewsCategory,UserInfo,NewsInfo

#如果希望用户直接访问，则不添加前缀
news_blueprint=Blueprint('news',__name__)

@news_blueprint.route('/')
def index():
    #查询分类，用于展示
    category_list=NewsCategory.query.all()

    #判断用户是否登录
    if 'user_id' in session:
        user=UserInfo.query.get(session['user_id'])
    else:
        user=None

    #查询点击量最高的6条数据==>select * from ... order by ... limit 0,6
    count_list=NewsInfo.query.order_by(NewsInfo.click_count.desc())[0:6]


    return render_template(
        'news/index.html',
        category_list=category_list,
        title='首页',
        user=user,
        count_list=count_list
    )

@news_blueprint.route('/newslist')
def newslist():
    #接收当前页码值
    page=int(request.args.get('page','1'))
    #查询数据并分页
    pagination=NewsInfo.query

    #接收分类的编号，进行指定分类的查询
    category_id=int(request.args.get('category_id','0'))
    if category_id:
        pagination=pagination.filter_by(category_id=category_id)

    pagination=pagination.order_by(NewsInfo.update_time.desc()).paginate(page,4,False)
    #获取当前页数据
    news_list=pagination.items
    #此处不需要总页数，因为界面上不需要页码链接

    #因为NewsInfo类型的对象，在js中是无法识别的，所以需要改成字典对象再返回
    news_list2=[]
    for news in news_list:
        news_dict={
            'id':news.id,
            'title':news.title,
            'summary':news.summary,
            'pic_url':news.pic_url,
            'user_avatar':news.user.avatar_url,
            'user_id':news.user_id,
            'user_nick_name':news.user.nick_name,
            'update_time':news.update_time,
            'category_id':news.category_id
        }
        news_list2.append(news_dict)


    return jsonify(
        page=page,
        news_list=news_list2
    )


    pass