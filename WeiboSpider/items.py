# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy



class UserInfoItem(scrapy.Item):
    # 用户ID.
    user_id = scrapy.Field()
    # 昵称.
    user_name = scrapy.Field()
    # 性别.
    gender = scrapy.Field()
    # 所在地.
    district = scrapy.Field()
    # 爬取时间. 年月日.
    crawl_date = scrapy.Field()

class FollowItem(scrapy.Item):
    user_id = scrapy.Field()
    # 所有关注的人.
    follow_list = scrapy.Field()
    size = scrapy.Field()
    # 爬取时间. 年月日.
    crawl_date = scrapy.Field()

class FanItem(scrapy.Item):
    user_id = scrapy.Field()
    # 所有粉丝.
    fan_list = scrapy.Field()
    size = scrapy.Field()
    # 爬取时间. 年月日.
    crawl_date = scrapy.Field()

class PostItem(scrapy.Item):
    user_id = scrapy.Field()
    # 所有微博.
    post_id = scrapy.Field()
    # 发布时间.
    publish_time = scrapy.Field()
    # 爬取时间. 年月日.
    crawl_date = scrapy.Field()

class TextItem(scrapy.Item):
    user_id = scrapy.Field()
    post_id = scrapy.Field()
    # 每条微博的文本.
    text = scrapy.Field()
    # 爬取时间. 年月日.
    crawl_date = scrapy.Field()

class ImageItem(scrapy.Field):
    user_id = scrapy.Field()
    post_id = scrapy.Field()
    # 每条微博的所有图片.
    image_list = scrapy.Field()
    size = scrapy.Field()
    # 爬取时间. 年月日.
    crawl_date = scrapy.Field()

class CommentItem(scrapy.Item):
    user_id = scrapy.Field()
    post_id = scrapy.Field()
    # 每条微博的所有评论.
    comment_list = scrapy.Field()
    size = scrapy.Field()
    # 爬取时间. 年月日.
    crawl_date = scrapy.Field()

class ForwardItem(scrapy.Item):
    user_id = scrapy.Field()
    post_id = scrapy.Field()
    # 每条微博的所有转发.
    forward_list = scrapy.Field()
    size = scrapy.Field()
    # 爬取时间. 年月日.
    crawl_date = scrapy.Field()

class ThumbupItem(scrapy.Item):
    user_id = scrapy.Field()
    post_id = scrapy.Field()
    # 每条微博的所有点赞.
    thumbup_list = scrapy.Field()
    size = scrapy.Field()
    # 爬取时间. 年月日.
    crawl_date = scrapy.Field()
