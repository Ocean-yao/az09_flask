from flask import Blueprint, render_template, jsonify
from flask import request
from flask import session
from models import db, NewsInfo, NewsCategory, UserInfo


# 如果希望用户直接访问，就不用加前缀
news_blueprint = Blueprint('news', __name__)


@news_blueprint.route('/')
def index():
    title = "首页-新经资讯"
    category_list = NewsCategory.query.all()
    count_list = NewsInfo.query.order_by(NewsInfo.click_count.desc())[0:6]
    if 'user_id' in session:
        user = UserInfo.query.get(session['user_id'])
    else:
        user = None

    return render_template('news/index.html',
                           title=title,
                           category_list=category_list,
                           user=user,
                           count_list=count_list
                           )

@news_blueprint.route('/newslist')
def newslist():

    # 接受页码值
    page = int(request.args.get('page', 1))

    # 对数据进行分页
    category_id = int(request.args.get('catagory_id', 0))

    pagination = NewsInfo.query

    if category_id:
        pagination = pagination.filter_by(category_id=category_id)

    pagination = pagination.order_by(NewsInfo.update_time.desc()).paginate(page, 4, False)

    # 当前内容
    news_list = pagination.items

    # 定义一个空列表
    news_list2 = []

    for news in news_list:
        news_dict = {
            'id': news.id,
            'pic_url': news.pic_url,
            'title': news.title,
            'summary': news.summary,
            'user_avatar': news.user.avatar_url,
            'user_id': news.user_id,
            'user_nick_name': news.user.nick_name,
            'update_time': news.update_time,
            'category_id': news.category_id
        }
        news_list2.append(news_dict)

    return jsonify(page=page, news_list=news_list2)


