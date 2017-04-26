# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sys, psycopg2, logging
from psycopg2 import errorcodes
from scrapy.mail import MailSender
from .items import UserInfoItem, FollowItem, FanItem, \
    PostItem, TextItem, ImageItem, CommentItem, ForwardItem, ThumbupItem



class WeibospiderPipeline(object):
    def __init__(self, settings):
        self.username = settings.get('POSTGRESQL_USERNAME')
        self.password = settings.get('POSTGRESQL_PASSWORD')
        self.host = settings.get('POSTGRESQL_HOST')
        self.database = settings.get('POSTGRESQL_DATABASE')
        self.table_name_dict = settings.get('TABLE_NAME_DICT')

        self.mail_enabled = settings.get('MAIL_ENABLED')
        if self.mail_enabled:
            self.mailer = MailSender.from_settings(settings)
            self.to_addr = settings.get('TO_ADDR')

        self.user_info_item_count = 1
        self.follow_item_count = 1
        self.fan_item_count = 1
        self.post_item_count = 1
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
                host = self.host,
                database = self.database
            )
            self.logger.info('Conneting to database successfully!')
        except psycopg2.Error as e:
            sys.exit('Failed to connect database. Returned: {0:s}'.format(errorcodes.lookup(e.pgcode)))

        # 如果表不存在，则首先建表。
        cursor = self.connector.cursor()
        try:
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS {0:s} (user_id varchar(20) PRIMARY KEY NOT NULL, user_name text NOT NULL, gender varchar(5) NOT NULL, district text NOT NULL, crawl_time date NOT NULL);'.format(
                    self.table_name_dict['user_info']
                )
            )
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS {0:s} (user_id varchar(20) PRIMARY KEY NOT NULL, follow_list text[] NOT NULL, crawl_time date NOT NULL);'.format(
                    self.table_name_dict['follow']
                )
            )
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS {0:s} (user_id varchar(20) PRIMARY KEY NOT NULL, fan_list text[] NOT NULL, crawl_time date NOT NULL);'.format(
                    self.table_name_dict['fan']
                )
            )
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS {0:s} (user_id varchar(20) PRIMARY KEY NOT NULL, post_id varchar(20) NOT NULL, publish_time timestamp NOT NULL, crawl_time date NOT NULL);'.format(
                    self.table_name_dict['post']
                )
            )
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS {0:s} (user_id varchar(20) NOT NULL, post_id varchar(20) NOT NULL, text text NOT NULL, crawl_time date NOT NULL, PRIMARY KEY(user_id, post_id));'.format(
                    self.table_name_dict['text']
                )
            )
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS {0:s} (user_id varchar(20) NOT NULL, post_id varchar(20) NOT NULL, image_list text[] NOT NULL, crawl_time date NOT NULL, PRIMARY KEY(user_id, post_id));'.format(
                    self.table_name_dict['image']
                )
            )
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS {0:s} (user_id varchar(20) NOT NULL, post_id varchar(20) NOT NULL, comment_list json NOT NULL, crawl_time date NOT NULL, PRIMARY KEY(user_id, post_id));'.format(
                    self.table_name_dict['comment']
                )
            )
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS {0:s} (user_id varchar(20) NOT NULL, post_id varchar(20) NOT NULL, forward_list json NOT NULL, crawl_time date NOT NULL, PRIMARY KEY(user_id, post_id));'.format(
                    self.table_name_dict['forward']
                )
            )
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS {0:s} (user_id varchar(20) NOT NULL, post_id varchar(20) NOT NULL, thumbup_list json NOT NULL, crawl_time date NOT NULL, PRIMARY KEY(user_id, post_id));'.format(
                    self.table_name_dict['thumbup']
                )
            )

            self.connector.commit()
            self.logger.info('Table check finished!')
        except psycopg2.Error as e:
            self.logger.error(
                'Table check failed. Returned: {0:s}.'.format(
                    errorcodes.lookup(e.pgcode)
                )
            )
        finally:
            cursor.close()

    def close_spider(self, spider):
        self.connector.close()

        if self.mail_enabled:
            self.mailer.send(
                to = self.to_addr,
                subject = '爬虫结束',
                body = '共抓取 {0:d} 条微博，{1:d} 条评论，{2:d} 条转发，{3:d} 条点赞'.format(
                    self.post_item_count,
                    self.comment_item_count,
                    self.forward_item_count,
                    self.thumbup_item_count
                ),
                charset = 'utf-8'
            )

    def process_item(self, item, spider):
        if isinstance(item, UserInfoItem):
            cursor = self.connector.cursor()
            try:
                statement = (
                    'INSERT INTO {0:s} (user_id, user_name, gender, district, crawl_time)'
                    'VALUES (%(user_id)s, %(user_name)s, %(gender)s, %(district)s, %(crawl_time)s);'
                ).format(self.table_name_dict['user_info'])
                cursor.execute(
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
                self.connector.rollback()
            finally:
                cursor.close()
        elif isinstance(item, FollowItem):
            cursor = self.connector.cursor()
            try:
                statement = (
                    'INSERT INTO {0:s} (user_id, follow_list, crawl_time)'
                    'VALUES (%(user_id)s, %(follow_list)s, %(crawl_time)s);'
                ).format(self.table_name_dict['follow'])
                cursor.execute(
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
                self.connector.rollback()
            finally:
                cursor.close()
        elif isinstance(item, FanItem):
            cursor = self.connector.cursor()
            try:
                statement = (
                    'INSERT INTO {0:s} (user_id, fan_list, crawl_time)'
                    'VALUES (%(user_id)s, %(fan_list)s, %(crawl_time)s);'
                ).format(self.table_name_dict['fan'])
                cursor.execute(
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
                self.connector.rollback()
            finally:
                cursor.close()
        elif isinstance(item, PostItem):
            cursor = self.connector.cursor()
            try:
                statement = (
                    'INSERT INTO {0:s} (user_id, post_id, publish_time, crawl_time)'
                    'VALUES (%(user_id)s, %(post_id)s, %(publish_time)s, %(crawl_time)s);'
                ).format(self.table_name_dict['post'])
                cursor.execute(
                    statement,
                    dict(item)
                )
                self.connector.commit()
                self.logger.info(
                    'Write a post item (user_id: {0:s} post_id: {1:s}) into database. Seq: {2:d}'.format(
                        item['user_id'],
                        item['post_id'],
                        self.post_item_count
                    )
                )
                self.post_item_count += 1
            except psycopg2.Error as e:
                self.logger.error(
                    'Failed to insert data into table {0:s}. Returned: {1:s}'.format(
                        self.table_name_dict['post'],
                        errorcodes.lookup(e.pgcode)
                    )
                )
                self.connector.rollback()
            finally:
                cursor.close()
        elif isinstance(item, TextItem):
            cursor = self.connector.cursor()
            try:
                statement = (
                    'INSERT INTO {0:s} (user_id, post_id, text, crawl_time)'
                    'VALUES (%(user_id)s, %(post_id)s, %(text)s, %(crawl_time)s);'
                ).format(self.table_name_dict['text'])
                cursor.execute(
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
                self.connector.rollback()
            finally:
                cursor.close()
        elif isinstance(item, ImageItem):
            cursor = self.connector.cursor()
            try:
                statement = (
                    'INSERT INTO {0:s} (user_id, post_id, image_list, crawl_time)'
                    'VALUES (%(user_id)s, %(post_id)s, %(image_list)s, %(crawl_time)s);'
                ).format(self.table_name_dict['image'])
                cursor.execute(
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
                self.connector.rollback()
            finally:
                cursor.close()
        elif isinstance(item, CommentItem):
            cursor = self.connector.cursor()
            try:
                statement = (
                    'INSERT INTO {0:s} (user_id, post_id, comment_list, crawl_time)'
                    'VALUES (%(user_id)s, %(post_id)s, %(comment_list)s, %(crawl_time)s);'
                ).format(
                    self.table_name_dict['comment']
                )
                cursor.execute(
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
                self.connector.rollback()
            finally:
                cursor.close()
        elif isinstance(item, ForwardItem):
            cursor = self.connector.cursor()
            try:
                statement = (
                    'INSERT INTO {0:s} (user_id, post_id, forward_list, crawl_time) '
                    'VALUES (%(user_id)s, %(post_id)s, %(forward_list)s, %(crawl_time)s);'
                ).format(self.table_name_dict['forward'])
                cursor.execute(
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
                self.connector.rollback()
            finally:cursor.close()
        elif isinstance(item, ThumbupItem):
            cursor = self.connector.cursor()
            try:
                statement = (
                    'INSERT INTO {0:s} (user_id, post_id, thumbup_list, crawl_time) '
                    'VALUES (%(user_id)s, %(post_id)s, %(thumbup_list)s, %(crawl_time)s);'
                ).format(self.table_name_dict['thumbup'])
                cursor.execute(
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
                self.connector.rollback()
            finally:
                cursor.close()

        return item
