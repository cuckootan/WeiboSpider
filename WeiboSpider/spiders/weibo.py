#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Jason'

import scrapy, json, re
from scrapy.spiders import CrawlSpider
from datetime import datetime, timedelta

from ..items import UserInfoItem, FollowItem, FanItem, \
    PostItem, TextItem, ImageItem, CommentItem, ForwardItem, ThumbupItem



class WeiboSpider(CrawlSpider):
    name = 'weibo'
    allowed_domains = ['weibo.cn']

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)

    def error_handler(self, failure):
        self.logger.error(repr(failure))

    # 发送爬取所有用户的基本信息, 关注的人, 粉丝的 requests.
    def __send_common_requests(self):
        # 从配置文件中获取所有 user_id.
        user_id_list = None
        if self.settings.get('SPEC_WEIBO_ENABLED'):
            weibo_spec_list = self.settings.get('SPEC_WEIBO_LIST')
            user_id_list = [user_id for user_id, post_id in weibo_spec_list]
        else:
            user_id_list = self.settings.get('CRAWLED_WEIBO_USER_ID_LIST')

        # 发送 requests.
        for user_id in user_id_list:

            yield scrapy.Request(
                url = 'http://weibo.cn/' + user_id,
                meta = {'user_id': user_id}
            )

            yield scrapy.Request(
                url = 'http://weibo.cn/' + user_id + '/info',
                meta = {'user_id': user_id},
                callback = self.parse_user_info,
                errback = self.error_handler
            )

            # follow_item 的结构为：{'user_id': xxx, 'follow_list': [1th_follow, 2th_follow, ...]}。
            follow_item = FollowItem(
                user_id = None,
                follow_list = None,
                size = None,
                crawl_time = None
            )
            follow_item['user_id'] = user_id
            follow_item['follow_list'] = []
            # fan_item 的结构为：{'user_id': xxx, 'fan_list': [1th_fan, 2th_fan, ...]}。
            fan_item = FanItem(
                user_id = None,
                fan_list = None,
                size = None,
                crawl_time = None
            )
            fan_item['user_id'] = user_id
            fan_item['fan_list'] = []

            # 生成关注的 Request 对象，用以爬取当前用户关注的人。
            yield scrapy.Request(
                url = 'http://weibo.cn/' + user_id + '/follow?page=1',
                meta = {'item': follow_item},
                callback = self.parse_follow,
                errback = self.error_handler
            )

            # 生成粉丝的 Request 对象，用以爬取当前用户的粉丝。
            yield scrapy.Request(
                url = 'http://weibo.cn/' + user_id + '/fans?page=1',
                meta = {'item': fan_item},
                callback = self.parse_fan,
                errback = self.error_handler
            )

    def start_requests(self):
        self.logger.info('start...')

        yield from self.__send_common_requests()

        if self.settings.get('SPEC_WEIBO_ENABLED'):
            for user_id, post_id in self.settings.get('SPEC_WEIBO_LIST'):
                # 生成指定微博的基本信息的 Request 对象.
                yield scrapy.Request(
                    url = 'http://weibo.cn/comment/' + re.split('_', post_id)[1],
                    meta = {'user_id': user_id, 'post_id': post_id},
                    callback = self.parse_single_post,
                    errback = self.error_handler
                )
        else:
            for user_id in self.settings.get('CRAWLED_WEIBO_USER_ID_LIST'):
                # 生成首条微博的基本信息的 Request 对象.
                yield scrapy.Request(
                    url = 'http://weibo.cn/' + user_id + '?filter=1&page=1',
                    meta = {'user_id': user_id, 'cnt': 0},
                    callback = self.parse_all_posts,
                    errback = self.error_handler
                )

    # 爬取当前用户的个人信息并返回，并且生成关注，粉丝，微博基本信息的 Requst对象。
    def parse_user_info(self, response):
        # user_info_item 的结构为：{'user_id': xxx, 'user_name': xxx, 'gender': xxx, 'district': xxx}。
        user_info_item = UserInfoItem(
            user_id = None,
            user_name = None,
            gender = None,
            district = None,
            crawl_time = None
        )

        div_selector = response.xpath('//div[@class = "c" and contains(text(), "昵称")]')
        user_info_item['user_id'] = response.meta['user_id']

        text = div_selector.xpath('text()').extract()
        for item in text:
            temp = re.split(':|：', item)

            if temp[0] == '昵称':
                user_info_item['user_name'] = temp[1]
            elif temp[0] == '性别':
                user_info_item['gender'] = temp[1]
            elif temp[0] == '地区':
                user_info_item['district'] = temp[1]

        user_info_item['crawl_time'] = datetime.now().replace(microsecond = 0)

        self.logger.info('user_id: {0:s}. Its user_info has been crawled.'.format(user_info_item['user_id']))
        yield user_info_item

    # 递归地爬取当前用户的所有关注的人，爬取结束后返回。
    def parse_follow(self, response):
        follow_item = response.meta['item']

        for table_selector in response.xpath('//table'):
            follow_item['follow_list'].append(table_selector.xpath('.//td[2]/a[1]/text()').extract_first())

            cnt = len(follow_item['follow_list'])
            self.logger.info('user_id: {0:s}, follower seq: {1:d}'.format(follow_item['user_id'], cnt))

            if self.settings.get('MAX_FOLLOW_COUNTS_PER_USER') and cnt >= int(self.settings.get('MAX_FOLLOW_COUNTS_PER_USER')):
                follow_item['size'] = cnt
                follow_item['crawl_time'] = datetime.now().replace(microsecond = 0)

                self.logger.info('user_id: {0:s}. All the followers have been crawled.'.format(follow_item['user_id']))
                yield follow_item
                return

        # 如果后面还有，则生成下一页关注人的 Request 对象。
        if response.xpath('//div[@id = "pagelist"]//a[contains(text(), "下页")]'):
            next_url = 'http://weibo.cn' + response.xpath('//div[@id = "pagelist"]/form/div/a[1]/@href').extract_first()
            request = scrapy.Request(
                url = next_url,
                meta = {'item': follow_item},
                callback = self.parse_follow,
                errback = self.error_handler
            )
            yield request
        # 否则，返回当前用户的所有的关注的人。
        else:
            follow_item['size'] = len(follow_item['follow_list'])
            follow_item['crawl_time'] = datetime.now().replace(microsecond = 0)

            self.logger.info('user_id: {0:s}. All the followers have been crawled.'.format(follow_item['user_id']))
            yield follow_item

    # 递归地爬取当前用户的所有粉丝，爬取结束后返回。
    def parse_fan(self, response):
        fan_item = response.meta['item']
        div_selector = response.xpath('//div[@class = "c" and table]')

        for table_selector in div_selector.xpath('table'):
            fan_item['fan_list'].append(table_selector.xpath('.//td[2]/a[1]/text()').extract_first())

            cnt = len(fan_item['fan_list'])
            self.logger.info('user_id: {0:s}, fan seq: {1:d}'.format(fan_item['user_id'], cnt))

            if self.settings.get('MAX_FAN_COUNTS_PER_USER') and cnt >= int(self.settings.get('MAX_FAN_COUNTS_PER_USER')):
                fan_item['size'] = cnt
                fan_item['crawl_time'] = datetime.now().replace(microsecond = 0)

                self.logger.info('user_id: {0:s}. All the fans have been crawled.'.format(fan_item['user_id']))
                yield fan_item
                return

        # 如果后面还有，则生成下一页粉丝的 Request 对象。
        if response.xpath('//div[@id = "pagelist"]//a[contains(text(), "下页")]'):
            next_url = 'http://weibo.cn' + response.xpath('//div[@id = "pagelist"]/form/div/a[1]/@href').extract_first()
            request = scrapy.Request(
                url = next_url,
                meta = {'item': fan_item},
                callback = self.parse_fan,
                errback = self.error_handler
            )
            yield request
        # 否则，返回当前用户的所有粉丝。
        else:
            fan_item['size'] = len(fan_item['fan_list'])
            fan_item['crawl_time'] = datetime.now().replace(microsecond = 0)

            self.logger.info('user_id: {0:s}. All the fans have been crawled.'.format(fan_item['user_id']))
            yield fan_item

    def __send_other_requests(self, user_id, post_id, image_start_url, forward_start_url, thumbup_start_url):
        # image_item 的结构为：{'user_id': xxx, 'post_id': xxx, 'image_list': [1th_image, 2nd_image, ...], 'size': xxx, 'crawl_time': xxx}.
        image_item = ImageItem(
            user_id = None,
            post_id = None,
            image_list = None,
            size = None,
            crawl_time = None
        )
        # forward_item 的结构为：{'user_id': xxx, 'post_id': xxx, 'forward_list': [json.dumps({'forward_user': 1th_user, 'forward_time': 1th_time}), json.dumps({'forward_user': 2nd_user, 'forward_time': 2nd_time}), ...], 'size': xxx, 'crawl_time': xxx}.
        forward_item = ForwardItem(
            user_id = None,
            post_id = None,
            forward_list = None,
            size = None,
            crawl_time = None
        )
        # thumbup_item 的结构为：{'user_id': xxx, 'post_id': xxx, 'thumbup_list': [json.dumps({'thumbup_user': 1th_user, 'thumbup_time': 1th_time}), json.dumps({'thumbup_user': 2nd_user, 'thumbup_time': 2nd_time}), ...], 'size': xxx, 'crawl_time': xxx}.
        thumbup_item = ThumbupItem(
            user_id = None,
            post_id = None,
            thumbup_list = None,
            size = None,
            crawl_time = None
        )

        image_item['user_id'] = user_id
        image_item['post_id'] = post_id
        image_item['image_list'] = []
        forward_item['user_id'] = user_id
        forward_item['post_id'] = post_id
        forward_item['forward_list'] = []
        thumbup_item['user_id'] = user_id
        thumbup_item['post_id'] = post_id
        thumbup_item['thumbup_list'] = []

        # 生成这条微博的第一张图片的 Request 对象。
        yield scrapy.Request(
            url = image_start_url,
            meta = {'item': image_item},
            priority = 1,
            callback = self.parse_image,
            errback = self.error_handler
        )
        # 生成这条微博的第一页转发的 Request 对象。
        yield scrapy.Request(
            url = forward_start_url,
            meta = {'item': forward_item},
            priority = 1,
            callback = self.parse_forward,
            errback = self.error_handler
        )
        # 生成这条微博的第一页点赞的 Request 对象。
        yield scrapy.Request(
            url = thumbup_start_url,
            meta = {'item': thumbup_item},
            priority = 1,
            callback = self.parse_thumbup,
            errback = self.error_handler
        )

    def parse_single_post(self, response):
        user_id = response.meta['user_id']
        post_id = response.meta['post_id']

        if not response.xpath('//div[@class = "c" and @id = "M_" and div[2]]'):
            self.logger.info('user_id: {0:s} post_id: {0:s}. No image exists.'.format(user_id, post_id))
            return
        image_start_url = 'http://weibo.cn' + response.xpath('//div[@class = "c" and @id = "M_"]/div[2]/a[1]/@href').extract_first()

        flag = True
        for span_selector in response.xpath('(//body/div[not(@class) and not(@id)])/span'):
            temp_str = span_selector.xpath('./a/text()').extract_first() if span_selector.xpath('./a') else span_selector.xpath('./text()').extract_first()
            if re.search('转发', temp_str):
                temp_list = re.findall(r'\d+', temp_str)
                if (not temp_list) or (temp_list[0] == '0'):
                    flag = False
                else:
                    forward_start_url = 'http://weibo.cn' + span_selector.xpath('./a/@href').extract_first()
            elif re.search('赞', temp_str):
                temp_list = re.findall(r'\d+', temp_str)
                if (not temp_list) or (temp_list[0] == '0'):
                    flag = False
                else:
                    thumbup_start_url = 'http://weibo.cn' + span_selector.xpath('./a/@href').extract_first()
            elif re.search('评论', temp_str):
                temp_list = re.findall(r'\d+', temp_str)
                if (not temp_list) or (temp_list[0] == '0'):
                    flag = False

        if not flag:
            self.logger.info('user_id: {0:s} post_id: {1:s}. No comment or forward or thumbup exists.'.format(user_id, post_id))
            return

        publish_time = response.xpath('//body/div[@class = "c" and @id = "M_"]/div[2]/span[@class = "ct"]/text()').extract_first()
        # datetime 类型.
        publish_time = self.__handle_time(self.__get_time(response.headers['date']), publish_time)

        user_id = response.meta['user_id']
        post_id = response.meta['post_id']

        post_item = PostItem(
            user_id = None,
            post_id = None,
            publish_time = None,
            crawl_time = None
        )
        post_item['user_id'] = user_id
        post_item['post_id'] = post_id
        post_item['publish_time'] = publish_time
        post_item['crawl_time'] = datetime.now().replace(microsecond = 0)

        # text_item 的结构体为: {'user_id': xxx, 'post_id': xxx, 'text': xxx, 'crawl_time': xxx}.
        text_item = TextItem(
            user_id = None,
            post_id = None,
            text = None,
            crawl_time = None
        )
        text_item['user_id'] = user_id
        text_item['post_id'] = post_id
        text_item['text'] = response.xpath('//body/div[@class = "c" and @id = "M_"]/div[1]/span[@class = "ctt"]/text()').extract_first()
        text_item['crawl_time'] = datetime.now().replace(microsecond = 0)

        self.logger.info('user_id: {0:s} post_id: {1:s}. Its post info and text have been crawled.'.format(user_id, post_id))
        yield post_item
        yield text_item

        # comment_item 的结构为：{'user_id': xxx, 'post_id': xxx, 'comment_list': [json.dumps({'comment_user': 1th_user, 'comment_text': 1th_text, 'comment_time': 1th_time}), json.dumps({'comment_user': 2nd_user, 'comment_text': 2nd_text, 'comment_time': 2nd_time}), ...], 'size': xxx, 'crawl_time': xxx}.
        comment_item = CommentItem(
            user_id = None,
            post_id = None,
            comment_list = None,
            size = None,
            crawl_time = None
        )
        comment_item['user_id'] = user_id
        comment_item['post_id'] = post_id
        comment_item['comment_list'] = []
        response.meta['item'] = comment_item

        yield from self.parse_comment(response)

        # 发送 image, forward, thumbup 的 request.
        yield from self.__send_other_requests(user_id, post_id, image_start_url, forward_start_url, thumbup_start_url)

    # 爬取当前用户的所有微博的基本信息以及文本。对于每一条微博，爬取完基本信息后以及文本后，返回这两者，然后生成这条微博相关的第一张图片，第一页评论, 第一页转发的 Request 对象。
    def parse_all_posts(self, response):
        user_id = response.meta['user_id']
        cnt = response.meta['cnt']

        for div_selector in response.xpath('//div[@class = "c" and @id and div]'):
            post_id = div_selector.xpath('@id').extract_first()
            publish_time = None

            # 如果存在图像.
            if div_selector.xpath('div[2]'):
                publish_time = div_selector.xpath('div[2]/span[@class = "ct"]/text()').extract_first()
                image_start_url = div_selector.xpath('div[2]/a[1]/@href').extract_first()
                flag = True

                for a_selector in div_selector.xpath('div[2]/a'):
                    temp_str = a_selector.xpath('text()').extract_first()
                    if not temp_str:
                        continue

                    if re.search('赞', temp_str):
                        #　如果点赞个数为 0.
                        temp_list = re.findall(r'\d+', temp_str)
                        if (not temp_list) or (temp_list[0] == '0'):
                            flag = False
                        else:
                            thumbup_start_url = re.split(r'(http://weibo.cn/attitude/[^/]+)', a_selector.xpath('@href').extract_first())[1] + '?#attitude'
                    elif re.search('转发', temp_str):
                        #　如果转发个数为 0.
                        temp_list = re.findall(r'\d+', temp_str)
                        if (not temp_list) or (temp_list[0] == '0'):
                            flag = False
                        else:
                            forward_start_url = a_selector.xpath('@href').extract_first()
                    elif re.search('评论', temp_str):
                        #　如果评论个数为 0.
                        temp_list = re.findall(r'\d+', temp_str)
                        if (not temp_list) or (temp_list[0] == '0'):
                            flag = False
                        else:
                            comment_start_url = a_selector.xpath('@href').extract_first()

                # 如果点赞个数为或者转发个数或者评论个数为 0，则放弃这条微博.
                if not flag:
                    continue
            # 如果不存在图像，则丢弃这条微博.
            else:
                continue

            publish_time = re.split('来自', publish_time)[0].strip()
            # dateime 类型.
            publish_time = self.__handle_time(self.__get_time(response.headers['date']), publish_time)

            post_item = PostItem(
                user_id = None,
                post_id = None,
                publish_time = None,
                crawl_time = None
            )
            post_item['user_id'] = user_id
            post_item['post_id'] = post_id
            post_item['publish_time'] = publish_time
            post_item['crawl_time'] = datetime.now().replace(microsecond = 0)

            # text_item 的结构体为: {'user_id': xxx, 'post_id': xxx, 'text': xxx, 'crawl_time': xxx}.
            text_item = TextItem(
                user_id = None,
                post_id = None,
                text = None,
                crawl_time = None
            )
            text_item['user_id'] = user_id
            text_item['post_id'] = post_id
            text_item['text'] = div_selector.xpath('div[1]/span[@class = "ctt"]/text()').extract_first()
            text_item['crawl_time'] = datetime.now().replace(microsecond = 0)

            # 返回当前用户的当前微博的信息与文本.
            cnt += 1
            yield post_item
            yield text_item

            # 发送 image, comemnt, forward, thumbup 的 request.
            yield from self.__send_other_requests(user_id, post_id, image_start_url, comment_start_url, forward_start_url, thumbup_start_url)

            cnt = len(post_item['post_list'])
            self.logger.info('user_id: {0:s}, post seq: {1:d}'.format(post_item['user_id'], cnt))

            if self.settings.get('MAX_POST_COUNTS_PER_USER') and cnt >= int(self.settings.get('MAX_POST_COUNTS_PER_USER')):
                self.logger.info('user_id: {0:s}. All the posts have been crawled.'.format(post_item['user_id']))
                return

        # 如果当前用户还存在其他微博，则继续爬取它们的基本信息以及文本。由于每条微博是一个 Item，在爬取每一条微博的基本信息和文本后就会返回，因此当后面不存在微博时，不需要另作返回。
        if response.xpath('//div[@id = "pagelist" and @class = "pa"]//a[contains(text(), "下页")]/@href'):
            next_url = 'http://weibo.cn' \
                       + response.xpath('//div[@id = "pagelist" and @class = "pa"]//a[contains(text(), "下页")]/@href').extract_first()
            request = scrapy.Request(
                url = next_url,
                meta = {'user_id': user_id, 'cnt': cnt},
                callback = self.parse_all_posts,
                errback = self.error_handler
            )
            yield request

    def __get_time(self, publish_time):
        return datetime.strptime(publish_time.decode('utf-8'), '%a, %d %b %Y %H:%M:%S %Z')

    def __handle_time(self, now_time, publish_time):
        if re.match(r'\d+分钟前', publish_time):
            return now_time - timedelta(minutes = int(re.findall('\d+', publish_time)[0]))
        elif re.match(r'今天', publish_time):
            temp_time = re.findall(r'\d+', publish_time)
            return datetime(
                year = now_time.date().year,
                month = now_time.date().month,
                day = now_time.date().day,
                hour = int(temp_time[0]),
                minute = int(temp_time[1])
            )
        else:
            temp_time = re.findall(r'\d+', publish_time)
            # x-x-x x:x
            if int(temp_time[0]) > 12:
                return datetime(
                    year = int(temp_time[0]),
                    month = int(temp_time[1]),
                    day = int(temp_time[2]),
                    hour = int(temp_time[3]),
                    minute = int(temp_time[4])
                )
            # x月x日 x:x
            else:
                return datetime(
                    year = now_time.date().year,
                    month = int(temp_time[0]),
                    day = int(temp_time[1]),
                    hour = int(temp_time[2]),
                    minute = int(temp_time[3])
                )

    # 递归地爬取某条微博的所有图片，爬取结束后返回。
    def parse_image(self, response):
        image_item = response.meta['item']

        div_selector = response.xpath('//div[@class = "c" and img]')
        if div_selector:
            image_item['image_list'].append(div_selector[0].xpath('img/@src').extract_first())
            image_item['size'] = len(image_item['image_list'])
            image_item['crawl_time'] = datetime.now().replace(microsecond = 0)

            self.logger.info('user_id: {0:s}, post_id: {1:s}. All the images have been crawled.'.format(image_item['user_id'], image_item['post_id']))
            yield image_item
            return

        div_selector = response.xpath('//div[@class = "c" and div[@class = "tc"]]')
        image_item['image_list'].append(div_selector[0].xpath('a/img/@src').extract_first())

        cnt = len(image_item['image_list'])
        self.logger.info('user_id: {0:s}, post_id: {1:s}, image seq: {2:d}'.format(image_item['user_id'], image_item['post_id'], cnt))

        if self.settings.get('MAX_IMAGE_COUNTS_PER_POST') and cnt >= int(self.settings.get('MAX_IMAGE_COUNTS_PER_POST')):
            image_item['size'] = cnt
            image_item['crawl_time'] = datetime.now().replace(microsecond = 0)

            self.logger.info('user_id: {0:s}, post_id: {1:s}. All the images have been crawled.'.format(image_item['user_id'], image_item['post_id']))
            yield image_item
            return

        # 如果后面还存在其他图片，则生成下一张图片的 Request 对象。
        if div_selector[0].xpath('div[@class = "tc"][2]/a[contains(text(), "下一张")]'):
            next_url = 'http://weibo.cn' + div_selector[0].xpath('div[@class = "tc"][2]/a/@href').extract_first()
            request = scrapy.Request(
                url = next_url,
                meta = {'item': image_item},
                priority = 1,
                callback = self.parse_image,
                errback = self.error_handler
            )
            yield request
        # 否则，返回这条微博的所有图像。
        else:
            image_item['size'] = len(image_item['image_list'])
            image_item['crawl_time'] = datetime.now().replace(microsecond = 0)

            self.logger.info('user_id: {0:s}, post_id: {1:s}. All the images have been crawled.'.format(image_item['user_id'], image_item['post_id']))
            yield image_item

    # 递归地爬取某条微博的所有评论，爬去结束后返回。
    def parse_comment(self, response):
        comment_item = response.meta['item']

        for div_selector in response.xpath('//div[@class = "c" and @id and a and span]'):
            # 不抽取 @ 某人的评论以及回复的内容。
            if div_selector.xpath('span[@class = "ctt" and contains(text(), "回复")]'):
                continue

            comment_user = div_selector.xpath('a[1]/text()').extract_first()
            comment_text = div_selector.xpath('span[@class = "ctt"]/text()').extract_first()
            comment_time = div_selector.xpath('span[@class = "ct"]/text()').extract_first()
            comment_time = str(self.__handle_time(self.__get_time(response.headers['date']), comment_time))

            comment_item['comment_list'].append({
                'comment_user': comment_user,
                'comment_text': comment_text,
                'comment_time': comment_time
            })

            cnt = len(comment_item['comment_list'])
            self.logger.info('user_id: {0:s}, post_id: {1:s}, comment seq: {2:d}'.format(comment_item['user_id'], comment_item['post_id'], cnt))

            if self.settings.get('MAX_COMMENT_COUNTS_PER_POST') and cnt >= int(self.settings.get('MAX_COMMENT_COUNTS_PER_POST')):
                comment_item['size'] = cnt
                comment_item['comment_list'] = json.dumps(comment_item['comment_list'])
                comment_item['crawl_time'] = datetime.now().replace(microsecond = 0)

                self.logger.info('user_id: {0:s}, post_id: {1:s}. All the comments have been crawled.'.format(comment_item['user_id'], comment_item['post_id']))
                yield comment_item
                return

        # 如果后面还存在着其他评论，则生成下一页评论的 Request 对象。
        if response.xpath('//div[@class = "pa" and @id = "pagelist"]//a[contains(text(), "下页")]'):
            next_url = 'http://weibo.cn' \
                       + response.xpath('//div[@class = "pa" and @id = "pagelist"]/form/div/a[1]/@href').extract_first()
            request = scrapy.Request(
                url = next_url,
                meta = {'item': comment_item},
                priority = 1,
                callback = self.parse_comment,
                errback = self.error_handler
            )
            yield request
        # 否则，返回这条微博的所有评论。
        else:
            comment_item['size'] = len(comment_item['comment_list'])
            comment_item['comment_list'] = json.dumps(comment_item['comment_list'])
            comment_item['crawl_time'] = datetime.now().replace(microsecond = 0)

            self.logger.info('user_id: {0:s}, post_id: {1:s}. All the comments have been crawled.'.format(comment_item['user_id'], comment_item['post_id']))
            yield comment_item

    # 递归地爬取某条微博的所有的转发，爬取结束后返回。
    def parse_forward(self, response):
        forward_item = response.meta['item']

        for div_selector in response.xpath('//div[@class="c"]'):
            if div_selector.xpath('span[@class="ct"]'):
                forward_user = div_selector.xpath('a/text()').extract_first()
                forward_time = re.split('来自', div_selector.xpath('span[@class="ct"]/text()').extract_first())[0].strip()
                forward_time = str(self.__handle_time(self.__get_time(response.headers['date']), forward_time))

                forward_item['forward_list'].append({
                    'forward_user': forward_user,
                    'forward_time': forward_time
                })

                cnt = len(forward_item['forward_list'])
                self.logger.info('user_id: {0:s}, post_id: {1:s}, forward seq: {2:d}'.format(forward_item['user_id'], forward_item['post_id'], cnt))

                if self.settings.get('MAX_FORWARD_COUNTS_PER_POST') and cnt >= int(self.settings.get('MAX_FORWARD_COUNTS_PER_POST')):
                    forward_item['size'] = cnt
                    forward_item['forward_list'] = json.dumps(forward_item['forward_list'])
                    forward_item['crawl_time'] = datetime.now().replace(microsecond = 0)

                    self.logger.info('user_id: {0:s}, post_id: {1:s}. All the forwards have been crawled.'.format(forward_item['user_id'], forward_item['post_id']))
                    yield forward_item
                    return

        # 如果后面还存在着其他转发，则生成下一页转发的 Request 对象。
        if response.xpath('//div[@class = "pa" and @id = "pagelist"]//a[contains(text(), "下页")]'):
            next_url = 'http://weibo.cn' \
                       + response.xpath('//div[@class = "pa" and @id = "pagelist"]/form/div/a[1]/@href').extract_first()
            request = scrapy.Request(
                url = next_url,
                meta = {'item': forward_item},
                priority = 1,
                callback = self.parse_forward,
                errback = self.error_handler
            )
            yield request
        # 否则，返回这条微博的所有的转发内容，然后生成第一页点赞的 Request 对象。之所以不在 parse_all_posts 里生成，是因为其中返回的 response 里没有正确的点赞 url（其中的 url 请求后相当于是点赞）。
        else:
            forward_item['size'] = len(forward_item['forward_list'])
            forward_item['forward_list'] = json.dumps(forward_item['forward_list'])
            forward_item['crawl_time'] = datetime.now().replace(microsecond = 0)

            self.logger.info('user_id: {0:s}, post_id: {1:s}. All the forwards have been crawled.'.format(forward_item['user_id'], forward_item['post_id']))
            yield forward_item

    # 爬取某条微博的所有点赞信息，爬取结束后返回。
    def parse_thumbup(self, response):
        thumbup_item = response.meta['item']

        for div_selector in response.xpath('//div[@class = "c"]'):
            if div_selector.xpath('span[@class = "ct"]'):
                thumbup_user = div_selector.xpath('a/text()').extract_first()
                thumbup_time = re.split('来自', div_selector.xpath('span[@class = "ct"]/text()').extract_first())[0].strip()
                thumbup_time = str(self.__handle_time(self.__get_time(response.headers['date']), thumbup_time))

                thumbup_item['thumbup_list'].append({
                    'thumbup_user': thumbup_user,
                    'thumbup_time': thumbup_time
                })

                cnt = len(thumbup_item['thumbup_list'])
                self.logger.info('user_id: {0:s}, post_id: {1:s}, thumbup seq: {2:d}'.format(thumbup_item['user_id'], thumbup_item['post_id'], cnt))

                if self.settings.get('MAX_THUMBUP_COUNTS_PER_POST') and cnt >= int(self.settings.get('MAX_THUMBUP_COUNTS_PER_POST')):
                    thumbup_item['size'] = cnt
                    thumbup_item['thumbup_list'] = json.dumps(thumbup_item['thumbup_list'])
                    thumbup_item['crawl_time'] = datetime.now().replace(microsecond = 0)

                    self.logger.info('user_id: {0:s}, post_id: {1:s}. All the thumbups have been crawled.'.format(thumbup_item['user_id'], thumbup_item['post_id']))
                    yield thumbup_item
                    return

        # 如果后面还存在着其他点赞，则生成下一页点赞的 Request 对象。
        if response.xpath('//div[@class = "pa" and @id = "pagelist"]//a[contains(text(), "下页")]'):
            next_url = 'http://weibo.cn' \
                       + response.xpath('//div[@class = "pa" and @id = "pagelist"]/form/div/a[1]/@href').extract_first()
            request = scrapy.Request(
                url = next_url,
                meta = {'item': thumbup_item},
                priority = 1,
                callback = self.parse_thumbup,
                errback = self.error_handler
            )
            yield request
        # 否则，返回该条微博的所有点赞信息。
        else:
            thumbup_item['size'] = len(thumbup_item['thumbup_list'])
            thumbup_item['thumbup_list'] = json.dumps(thumbup_item['thumbup_list'])
            thumbup_item['crawl_time'] = datetime.now().replace(microsecond = 0)

            self.logger.info('user_id: {0:s}, post_id: {1:s}. All the thumbups have been crawled.'.format(thumbup_item['user_id'], thumbup_item['post_id']))
            yield thumbup_item
