# 整体思路：写出通用默认项，再在后面的developconfig中写入修改值

import redis
import os

class Config(object):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql://name:password@host:port/database'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # redis配置
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 9
    # session
    SECRET_KEY = "itheima"
    # flask_session的配置信息
    SESSION_TYPE = "redis"  # 指定 session 保存到 redis 中
    SESSION_USE_SIGNER = True  # 让 cookie 中的 session_id 被加密签名处理
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)  # 使用 redis 的实例
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 14  # session 的有效期，单位是秒
    #__file__==>config.py
    #os.path.abspath（）是绝对路径，返回了/home/python/Desktop/sz09_flask/xjzx/config.py
    #os.path.dirname返回的是文件所在的文件夹的名字==》/home/python/Desktop/sz09_flask/xjzx
    #BASE_DIR只得就是项目的路径
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # 七牛云配置,需要将信息进行更改，个人中心秘钥管理
    QINIU_AK = '1zd3yuMF4Yy5sfVtO7L_r_37BHBtAT7coE9GLTKT'
    QINIU_SK = 'D_HH8V7aRe96xhijYKJCVUHdvaZamX0myDxsSn9a'
    QINIU_BUCKET = 'itcast20171104'
    QINIU_URL = 'http://oyvzbpqij.bkt.clouddn.com/'


class DevelopConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/xjzx9'


