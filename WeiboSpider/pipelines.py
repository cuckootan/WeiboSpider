# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sys, psycopg2, logging
from psycopg2 import errorcodes
from .send_email import EmailSender
from .items import UserInfoItem, FollowItem, FanItem, \
    PostInfoItem, TextItem, ImageItem, CommentItem, ForwardItem, ThumbupItem



class WeibospiderPipeline(object):
    def __init__(self, settings):
        self.username = settings.get('POSTGRESQL_USERNAME')
        self.password = settings.get('POSTGRESQL_PASSWORD')
        self.database = settings.get('POSTGRESQL_DATABASE')
        self.table_name_dict = settings.get('TABLE_NAME_DICT')
       
        self.mail_enabled = settings.get('MAIL_ENABLED')
        if self.mail_enabled:
            self.emailer = EmailSender()
            self.emailer.from_settings(settings)
            self.to_addr = settings.get('TO_ADDR')

        self.user_info_item_count = 1
        self.follow_item_count = 1
        self.fan_item_count = 1
        self.post_info_item_count = 1
        self.text_item_count = 1
        self.image_item_count = 1
        self.comment_item_count = 1
        self.forward_item_count = 1
        self.thumbup_item_count = 1

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            settings = crawler.settings
        )

    def open_spider(self, spider):
        # 连接到数据库。
        try:
            self.connector = psycopg2.connect(
                user = self.username,
                password = self.password,
                database = self.database
            )
            self.cursor = self.connector.cursor()
            self.logger.info('Conneting to database successfully!')
        except psycopg2.Error as e:
            sys.exit('Failed to connect database. Returned: {0:s}'.format(errorcodes.lookup(e.pgcode)))

        # 如果表不存在，则首先建表。
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS {0:s} (user_id varchar(20), user_name text, gender varchar(5), district text);'.format(
                self.table_name_dict['user_info']
            )
        )
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS {0:s} (user_id varchar(20), follow_list text[]);'.format(
                self.table_name_dict['follow']
            )
        )
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS {0:s} (user_id varchar(20), fan_list text[]);'.format(
                self.table_name_dict['fan']
            )
        )
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS {0:s} (user_id varchar(20), post_id varchar(20), publish_time text);'.format(
                self.table_name_dict['post_info']
            )
        )
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS {0:s} (user_id varchar(20), post_id varchar(20), text text);'.format(
                self.table_name_dict['text']
            )
        )
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS {0:s} (user_id varchar(20), post_id varchar(20), image_list text[]);'.format(
                self.table_name_dict['image']
            )
        )
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS {0:s} (user_id varchar(20), post_id varchar(20), comment_list json);'.format(
                self.table_name_dict['comment']
            )
        )
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS {0:s} (user_id varchar(20), post_id varchar(20), forward_list json);'.format(
                self.table_name_dict['forward']
            )
        )
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS {0:s} (user_id varchar(20), post_id varchar(20), thumbup_list json);'.format(
                self.table_name_dict['thumbup']
            )
        )
        self.connector.commit()
        self.logger.info('Table check finished!')

    def close_spider(self, spider):
        self.cursor.close()
        self.connector.close()
        
        if self.mail_enabled:
            self.emailer.send(
                to_addr = self.to_addr,
                subject = '爬虫结束',
                body = '共抓取 {0:d} 条微博，{1:d} 条评论，{2:d} 条转发，{3:d} 条点赞'.format(
                    self.post_info_item_count,
                    self.comment_item_count,
                    self.forward_item_count,
                    self.thumbup_item_count
                ),
                charset = 'utf-8'
            )

    def process_item(self, item, spider):
        if isinstance(item, UserInfoItem):
            try:
                statement = (
                    'INSERT INTO {0:s} (user_id, user_name, gender, district)'
                    'VALUES (%(user_id)s, %(user_name)s, %(gender)s, %(district)s);'
                ).format(self.table_name_dict['user_info'])
                self.cursor.execute(
                    statement,
                    dict(item)
                )
                self.connector.commit()
                self.logger.info(
                    'Write a user_info item (user_id: {0:s}) into database. Seq: {1:d}'.format(
                        item['user_id'],
                        self.user_info_item_count
                    )
                )
                self.user_info_item_count += 1
            except psycopg2.Error as e:
                self.logger.error(
                    'Failed to insert data into table {0:s}. Returned: {1:s}'.format(
                        self.table_name_dict['user_info'],
                        errorcodes.lookup(e.pgcode)
                    )
                )
        elif isinstance(item, FollowItem):
            try:
                statement = (
                    'INSERT INTO {0:s} (user_id, follow_list)'
                    'VALUES (%(user_id)s, %(follow_list)s);'
                ).format(self.table_name_dict['follow'])
                self.cursor.execute(
                    statement,
                    dict(item)
                )
                self.connector.commit()
                self.logger.info(
                    'Write a follow item (user_id: {0:s}) including {1:d} followers into database. Seq: {2:d}'.format(
                        item['user_id'],
                        item['size'],
                        self.follow_item_count
                    )
                )
                self.follow_item_count += 1
            except psycopg2.Error as e:
                self.logger.error(
                    'Failed to insert data into table {0:s}. Returned: {1:s}'.format(
                        self.table_name_dict['follow'],
                        errorcodes.lookup(e.pgcode)
                    )
                )
        elif isinstance(item, FanItem):
            try:
                statement = (
                    'INSERT INTO {0:s} (user_id, fan_list)'
                    'VALUES (%(user_id)s, %(fan_list)s);'
                ).format(self.table_name_dict['fan'])
                self.cursor.execute(
                    statement,
                    dict(item)
                )
                self.connector.commit()
                self.logger.info(
                    'Write a fan item (user_id: {0:s}) including {1:d} fans into database. Seq: {2:d}'.format(
                        item['user_id'],
                        item['size'],
                        self.fan_item_count
                    )
                )
                self.fan_item_count += 1
            except psycopg2.Error as e:
                self.logger.error(
                    'Failed to insert data into table {0:s}. Returned: {1:s}'.format(
                        self.table_name_dict['fan'],
                        errorcodes.lookup(e.pgcode)
                    )
                )
        elif isinstance(item, PostInfoItem):
            try:
                statement = (
                    'INSERT INTO {0:s} (user_id, post_id, publish_time)'
                    'VALUES (%(user_id)s, %(post_id)s, %(publish_time)s);'
                ).format(self.table_name_dict['post_info'])
                self.cursor.execute(
                    statement,
                    dict(item)
                )
                self.connector.commit()
                self.logger.info(
                    'Write a post_info item (user_id: {0:s} post_id: {1:s}) into database. Seq: {2:d}'.format(
                        item['user_id'],
                        item['post_id'],
                        self.post_info_item_count
                    )
                )
                self.post_info_item_count += 1
            except psycopg2.Error as e:
                self.logger.error(
                    'Failed to insert data into table {0:s}. Returned: {1:s}'.format(
                        self.table_name_dict['post_info'],
                        errorcodes.lookup(e.pgcode)
                    )
                )
        elif isinstance(item, TextItem):
            try:
                statement = (
                    'INSERT INTO {0:s} (user_id, post_id, text)'
                    'VALUES (%(user_id)s, %(post_id)s, %(text)s);'
                ).format(self.table_name_dict['text'])
                self.cursor.execute(
                    statement,
                    dict(item)
                )
                self.connector.commit()
                self.logger.info(
                    'Write a text item (user_id: {0:s} post_id: {1:s}) into database. Seq: {2:d}'.format(
                        item['user_id'],
                        item['post_id'],
                        self.text_item_count
                    )
                )
                self.text_item_count += 1
            except psycopg2.Error as e:
                self.logger.error(
                    'Failed to insert data into table {0:s}. Returned: {1:s}'.format(
                        self.table_name_dict['text'],
                        errorcodes.lookup(e.pgcode)
                    )
                )
        elif isinstance(item, ImageItem):
            try:
                statement = (
                    'INSERT INTO {0:s} (user_id, post_id, image_list)'
                    'VALUES (%(user_id)s, %(post_id)s, %(image_list)s);'
                ).format(self.table_name_dict['image'])
                self.cursor.execute(
                    statement,
                    dict(item)
                )
                self.connector.commit()
                self.logger.info(
                    'Write an image item (user_id: {0:s} post_id: {1:s}) including {2:d} images into database. Seq: {3:d}'.format(
                        item['user_id'],
                        item['post_id'],
                        item['size'],
                        self.image_item_count
                    )
                )
                self.image_item_count += 1
            except psycopg2.Error as e:
                self.logger.error(
                    'Failed to insert data into table {0:s}. Returned: {1:s}'.format(
                        self.table_name_dict['image'],
                        errorcodes.lookup(e.pgcode)
                    )
                )
        elif isinstance(item, CommentItem):
            try:
                statement = (
                    'INSERT INTO {0:s} (user_id, post_id, comment_list)'
                    'VALUES (%(user_id)s, %(post_id)s, %(comment_list)s);'
                ).format(
                    self.table_name_dict['comment']
                )
                self.cursor.execute(
                    statement,
                    dict(item)
                )
                self.connector.commit()
                self.logger.info(
                    'Write a comment item (user_id: {0:s} post_id: {1:s}) including {2:d} comments into database. Seq: {3:d}'.format(
                        item['user_id'],
                        item['post_id'],
                        item['size'],
                        self.comment_item_count
                    )
                )
                self.comment_item_count += 1
            except psycopg2.Error as e:
                self.logger.error(
                    'Failed to insert data into table {0:s}. Returned: {1:s}'.format(
                        self.table_name_dict['comment'],
                        errorcodes.lookup(e.pgcode)
                    )
                )
        elif isinstance(item, ForwardItem):
            try:
                statement = (
                    'INSERT INTO {0:s} (user_id, post_id, forward_list) '
                    'VALUES (%(user_id)s, %(post_id)s, %(forward_list)s);'
                ).format(self.table_name_dict['forward'])
                self.cursor.execute(
                    statement,
                    dict(item)
                )
                self.connector.commit()
                self.logger.info(
                    'Write a forward item (user_id: {0:s} post_id: {1:s}) including {2:d} forwards into database. Seq: {3:d}'.format(
                        item['user_id'],
                        item['post_id'],
                        item['size'],
                        self.forward_item_count
                    )
                )
                self.forward_item_count += 1
            except psycopg2.Error as e:
                self.logger.error(
                    'Failed to insert data into table {0:s}. Returned: {1:s}'.format(
                        self.table_name_dict['forward'],
                        errorcodes.lookup(e.pgcode)
                    )
                )
        elif isinstance(item, ThumbupItem):
            try:
                statement = (
                    'INSERT INTO {0:s} (user_id, post_id, thumbup_list) '
                    'VALUES (%(user_id)s, %(post_id)s, %(thumbup_list)s);'
                ).format(self.table_name_dict['thumbup'])
                self.cursor.execute(
                    statement,
                    dict(item)
                )
                self.connector.commit()
                self.logger.info(
                        'Write a thumb-up item (user_id: {0:s} post_id: {1:s}) including {2:d} thumbups into database. Seq: {3:d}'.format(
                            item['user_id'],
                            item['post_id'],
                            item['size'],
                            self.thumbup_item_count
                        )
                )
                self.thumbup_item_count += 1
            except psycopg2.Error as e:
                self.logger.error(
                    'Failed to insert data into table {0:s}. Returned: {1:s}'.format(
                        self.table_name_dict['thumbup'],
                        errorcodes.lookup(e.pgcode)
                    )
                )

        return item
