from flask import Blueprint

# 如果希望用户直接访问，就不用加前缀
news_blueprint = Blueprint('news',__name__)