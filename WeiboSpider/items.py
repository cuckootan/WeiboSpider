# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy



class UserInfoItem(scrapy.Item):
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    gender = scrapy.Field()
    district = scrapy.Field()

class FollowListItem(scrapy.Item):
    follow_list = scrapy.Field()

class FanListItem(scrapy.Item):
    fan_list = scrapy.Field()

class PostInfoItem(scrapy.Item):
    # 作者昵称。
    user_name = scrapy.Field()
    # 微博 ID。
    post_id = scrapy.Field()
    # 作者发布时间。
    publish_time = scrapy.Field()

class TextItem(scrapy.Item):
    user_name = scrapy.Field()
    post_id = scrapy.Field()
    text = scrapy.Field()

class ImageListItem(scrapy.Field):
    user_name = scrapy.Field()
    post_id = scrapy.Field()
    image_list = scrapy.Field()

class CommentListItem(scrapy.Item):
    user_name = scrapy.Field()
    post_id = scrapy.Field()
    comment_list = scrapy.Field()

class ForwardListItem(scrapy.Item):
    user_name = scrapy.Field()
    post_id = scrapy.Field()
    forward_list = scrapy.Field()

class ThumbupListItem(scrapy.Item):
    user_name = scrapy.Field()
    post_id = scrapy.Field()
    thumbup_list = scrapy.Field()