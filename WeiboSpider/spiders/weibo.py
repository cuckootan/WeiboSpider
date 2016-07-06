# -*- coding: utf-8 -*-

import scrapy, json, re
from scrapy.spiders import CrawlSpider

from ..items import UserInfoItem, FollowItem, FanItem, \
    PostInfoItem, TextItem, ImageItem, CommentItem, ForwardItem, ThumbupItem



class WeiboSpider(CrawlSpider):
    name = 'weibo'
    allowed_domains = ['weibo.cn']

    def start_requests(self):
        print('start...')

        yield scrapy.Request(
            url = 'http://weibo.cn/3592470455/info',
            meta = {'user_id': '3592470455'},
            callback = self.parse_user_info
        )

    # 爬取当前用户的个人信息并返回， 并且生成关注， 粉丝， 微博基本信息的 Requst对象。
    def parse_user_info(self, response):
        # user_info_item 的结构为： {'user_id': xxx, 'user_name': xxx, 'gender': xxx, 'district': xxx}。
        user_info_item = UserInfoItem(
            user_id = None,
            user_name = None,
            gender = None,
            district = None
        )

        user_info_item['user_id'] = response.meta['user_id']

        for div_selector in response.xpath('//div[@class="c"]'):
            if div_selector.xpath('text()') and div_selector.xpath('text()').extract_first()[:2] == '昵称':
                break

        user_info_item['user_name'] = div_selector.xpath('text()[1]').extract_first()[3:]
        user_info_item['gender'] = div_selector.xpath('text()[3]').extract_first()[3:]
        user_info_item['district'] = div_selector.xpath('text()[4]').extract_first()[3:]

        # 爬取当前用户的个人信息结束， 返回。
        yield user_info_item

        # follow_item 的结构为： {'user_id': xxx, 'follow_list': [1th_follow, 2th_follow, ...]}。
        follow_item = FollowItem(
            user_id = None,
            follow_list = None
        )
        follow_item['user_id'] = user_info_item['user_id']
        follow_item['follow_list'] = []
        # fan_item 的结构为： {'user_id': xxx, 'fan_list': [1th_fan, 2th_fan, ...]}。
        fan_item = FanItem(
            user_id = None,
            fan_list = None
        )
        fan_item['user_id'] = user_info_item['user_id']
        fan_item['fan_list'] = []

        # 生成关注的 Request 对象，用以爬取当前用户关注的人。
        yield scrapy.Request(
            url = 'http://weibo.cn/3592470455/follow?page=1',
            meta = {'item': follow_item},
            callback = self.parse_follow
        )

        # 生成粉丝的 Request 对象，用以爬取当前用户的粉丝。
        yield scrapy.Request(
            url = 'http://weibo.cn/3592470455/fans?page=1',
            meta = {'item': fan_item},
            callback = self.parse_fan
        )

        # 生成微博基本信息的 Request 对象，用以爬取当前用户的所有微博的基本信息。
        yield scrapy.Request(
            url = 'http://weibo.cn/3592470455/profile?page=1',
            meta = {'user_id': user_info_item['user_id']},
            callback = self.parse_post_info
        )

    # 递归地爬取当前用户的所有关注的人， 爬取结束后返回。
    def parse_follow(self, response):
        follow_item = response.meta['item']

        for table_selector in response.xpath('/html/body/table'):
            follow_item['follow_list'].append(table_selector.xpath('tr/td[2]/a[1]/text()').extract_first())

        # 如果后面还有， 则生成下一页关注人的 Request 对象。
        if response.xpath('//*[@id="pagelist"]') \
                and response.xpath('//*[@id="pagelist"]/form/div/a[1]/text()').extract_first() == '下页':
            next_url = 'http://weibo.cn' + response.xpath('//*[@id="pagelist"]/form/div/a[1]/@href').extract_first()
            yield scrapy.Request(
                url = next_url,
                meta = {'item': follow_item},
                callback = self.parse_follow
            )
        # 否则， 返回当前用户的所有的关注的人。
        else:
            yield follow_item

    # 递归地爬取当前用户的所有粉丝， 爬取结束后返回。
    def parse_fan(self, response):
        fan_item = response.meta['item']

        for div_selector in response.xpath('/html/body/div[@class="c"]'):
            if div_selector.xpath('table'):
                break

        for table_selector in div_selector.xpath('table'):
            fan_item['fan_list'].append(table_selector.xpath('tr/td[2]/a[1]/text()').extract_first())

        # 如果后面还有， 则生成下一页粉丝的 Request 对象。
        if response.xpath('//*[@id="pagelist"]') \
                and response.xpath('//*[@id="pagelist"]/form/div/a[1]/text()').extract_first() == '下页':
            next_url = 'http://weibo.cn' + response.xpath('//*[@id="pagelist"]/form/div/a[1]/@href').extract_first()
            yield scrapy.Request(
                url = next_url,
                meta = {'item': fan_item},
                callback = self.parse_fan
            )
        # 否则， 返回当前用户的所有粉丝。
        else:
            yield fan_item

    # 爬取当前用户的所有微博的基本信息以及文本。 对于每一条微博， 爬取完基本信息后以及文本后， 返回这两者， 然后生成这条微博相关的第一张图片， 第一页评论， 第一页转发的 Request 对象。
    def parse_post_info(self, response):
        for div_selector in response.xpath('//div[@class="c"]'):
            if div_selector.xpath('@id'):
                # 转发的微博, 不爬取。
                if div_selector.xpath('div[1]/span[1]') \
                        and div_selector.xpath('div[1]/span[1]/text()').extract_first()[:2] == '转发':
                    continue

                post_info_item = PostInfoItem(
                    user_id = None,
                    post_id = None,
                    publish_time = None
                )
                post_info_item['user_id'] = response.meta['user_id']
                post_info_item['post_id'] = div_selector.xpath('@id').extract_first()

                text_item = TextItem(
                    user_id = None,
                    post_id = None,
                    text = None
                )
                text_item['user_id'] = post_info_item['user_id']
                text_item['post_id'] = post_info_item['post_id']
                text_item['text'] = div_selector.xpath('div[1]/span[@class="ctt"]/text()').extract_first()

                # 如果存在图像。
                if div_selector.xpath('div[2]'):
                    post_info_item['publish_time'] = div_selector.xpath('div[2]/span[@class="ct"]/text()').extract_first()

                    for a_selector in div_selector.xpath('div[2]/a'):
                        temp_str = a_selector.xpath('text()').extract_first()

                        if not temp_str:
                            image_start_url = a_selector.xpath('@href').extract_first()
                        elif temp_str[:2] == '转发':
                            forward_start_url = a_selector.xpath('@href').extract_first()
                        elif temp_str[:2] == '评论':
                            comment_start_url = a_selector.xpath('@href').extract_first()
                else:
                    post_info_item['publish_time'] = div_selector.xpath('div[1]/span[@class="ct"]/text()').extract_first()
                    image_start_url = None

                    for a_selector in div_selector.xpath('div[1]/a'):
                        temp_str = a_selector.xpath('text()').extract_first()
                        if temp_str[:2] == '转发':
                            forward_start_url = a_selector.xpath('@href').extract_first()
                        elif temp_str[:2] == '评论':
                            comment_start_url = a_selector.xpath('@href').extract_first()

                post_info_item['publish_time'] = re.split('来自', post_info_item['publish_time'])[0].strip()

                # 返回当前用户的当前微博的基本信息以及文本。
                yield post_info_item
                yield text_item

                # comment_item 的结构为： {'user_id': xxx, 'post_id': xxx, 'comment_list': [json.dumps({'comment_user': 1th_user, 'comment_text': 1th_text, 'comment_time': 1th_time}), json.dumps({'comment_user': 2nd_user, 'comment_text': 2nd_text, 'comment_time': 2nd_time}), ...]}。
                comment_item = CommentItem(
                    user_id = None,
                    post_id = None,
                    comment_list = None
                )
                # forward_item 的结构为： {'user_id': xxx, 'post_id': xxx, 'forward_list': [json.dumps({'forward_user': 1th_user, 'forward_time': 1th_time}), json.dumps({'forward_user': 2nd_user, 'forward_time': 2nd_time}), ...]}。
                forward_item = ForwardItem(
                    user_id = None,
                    post_id = None,
                    forward_list = None
                )

                comment_item['user_id'] = post_info_item['user_id']
                comment_item['post_id'] = post_info_item['post_id']
                comment_item['comment_list'] = []
                forward_item['user_id'] = post_info_item['user_id']
                forward_item['post_id'] = post_info_item['post_id']
                forward_item['forward_list'] = []

                # 如果存在图片， 则生成者条微博的第一张图片的 Request 对象。
                if image_start_url:
                    # image_item 的结构为： {'user_id': xxx, 'post_id': xxx, 'image_list': [1th_image, 2nd_image, ...]}。
                    image_item = ImageItem(
                        user_id = None,
                        post_id = None,
                        image_list = None
                    )

                    image_item['user_id'] = post_info_item['user_id']
                    image_item['post_id'] = post_info_item['post_id']
                    image_item['image_list'] = []

                    yield scrapy.Request(
                        url = image_start_url,
                        meta = {'item': image_item},
                        callback = self.parse_image
                    )

                # 生成这条微博的第一页评论的 Request 对象。
                yield scrapy.Request(
                    url = comment_start_url,
                    meta = {'item': comment_item},
                    callback = self.parse_comment
                )

                # 生成这条微博的第一页转发的 Request 对象。
                yield scrapy.Request(
                    url = forward_start_url,
                    meta = {'item': forward_item},
                    callback = self.parse_forward
                )

        # 如果当前用户还存在其他微博， 则继续爬取它们的基本信息以及文本。由于每条微博是一个 Item， 在爬取每一条微博的基本信息和文本后就会返回，因此当后面不存在微博时， 不需要另作返回。
        if response.xpath('//div[@class="pa" and @id="pagelist"]') \
                and response.xpath('//div[@class="pa" and @id="pagelist"]/form/div/a[1]/text()').extract_first() == '下页':
            next_url = 'http://weibo.cn' \
                       + response.xpath('//div[@class="pa" and @id="pagelist"]/form/div/a[1]/@href').extract_first()
            yield scrapy.Request(
                url = next_url,
                meta = {'user_id': post_info_item['user_id']},
                callback = self.parse_post_info
            )

    # 递归地爬取某条微博的所有图片， 爬取结束后返回。
    def parse_image(self, response):
        image_item = response.meta['item']

        for div_selector in response.xpath('/html/body/div[@class="c"]'):
            # 如果只有一张图片。
            if div_selector.xpath('img'):
                image_item['image_list'].append(div_selector.xpath('img/@src').extract_first())
                yield

            if div_selector.xpath('a') and div_selector.xpath('a/img'):
                break

        image_item['image_list'].append(div_selector.xpath('a[1]/img/@src').extract_first())

        # 如果后面还存在其他图片， 则生成下一张图片的 Request 对象。
        if div_selector.xpath('div[2]/a[1]/text()').extract_first() == '下一张':
            next_url = 'http://weibo.cn' + div_selector.xpath('div[2]/a[1]/@href').extract_first()
            yield scrapy.Request(
                url = next_url,
                meta = {'item': image_item},
                callback = self.parse_image
            )
        # 否则， 返回这条微博的所有图像。
        else:
            yield image_item

    # 递归地爬取某条微博的所有评论， 爬去结束后返回。
    def parse_comment(self, response):
        comment_item = response.meta['item']

        for div_selector in response.xpath('/html/body/div[@class="c"]'):
            if div_selector.xpath('@id') and div_selector.xpath('@id').extract_first()[0] == 'C':
                comment_user = div_selector.xpath('a[1]/text()').extract_first()

                # 不抽取 @ 某人的评论以及回复的内容。
                if div_selector.xpath('span[@class="ctt"]/a') or \
                    div_selector.xpath('span[@class="ctt"]/text()[1]').extract_first() == '"回复"':
                    continue

                comment_text = div_selector.xpath('span[@class="ctt"]/text()').extract_first()
                comment_time = div_selector.xpath('span[@class="ct"]/text()').extract_first()

                comment_item['comment_list'].append(json.dumps({
                    'comment_user': comment_user,
                    'comment_text': comment_text,
                    'comment_time': comment_time
                }))

        # 如果后面还存在着其他评论， 则生成下一页评论的 Request 对象。
        if response.xpath('//div[@class="pa" and @id="pagelist"]') \
                and response.xpath('//div[@class="pa" and @id="pagelist"]/form/div/a[1]/text()').extract_first() == '下页':
            next_url = 'http://weibo.cn' \
                       + response.xpath('//div[@class="pa" and @id="pagelist"]/form/div/a[1]/@href').extract_first()
            yield scrapy.Request(
                url = next_url,
                meta = {'item': comment_item},
                callback = self.parse_comment
            )
        # 否则， 返回这条微博的所有评论。
        else:
            yield comment_item

    # 递归地爬取某条微博的所有的转发， 爬取结束后返回。
    def parse_forward(self, response):
        forward_item = response.meta['item']

        for div_selector in response.xpath('/html/body/div[@class="c"]'):
            if div_selector.xpath('span[@class="ct"]'):
                forward_user = div_selector.xpath('a/text()').extract_first()
                forward_time = re.split('来自', div_selector.xpath('span[@class="ct"]/text()').extract_first())[0].strip()

                forward_item['forward_list'].append(json.dumps({
                    'forward_user': forward_user,
                    'forward_time': forward_time
                }))

        # 如果后面还存在着其他转发， 则生成下一页转发的 Request 对象。
        if response.xpath('//div[@class="pa" and @id="pagelist"]') \
                and response.xpath('//div[@class="pa" and @id="pagelist"]/form/div/a[1]/text()').extract_first() == '下页':
            next_url = 'http://weibo.cn' \
                       + response.xpath('//div[@class="pa" and @id="pagelist"]/form/div/a[1]/@href').extract_first()
            yield scrapy.Request(
                url = next_url,
                meta = {'item': forward_item},
                callback = self.parse_forward
            )
        # 否则， 返回这条微博的所有的转发内容， 然后生成第一页点赞的 Request 对象。之所以不在 parse_post_info 里生成，是因为其中返回的 response 里没有正确的点赞 url（其中的 url 请求后相当于是点赞）。
        else:
            yield forward_item

            for div_selector in response.xpath('/html/body/div'):
                if div_selector.xpath('span[@class="pms"]'):
                    break

            # thumbup_item 的结构为： {'user_id': xxx, 'post_id': xxx, 'thumbup_list': [json.dumps({'thumbup_user': 1th_user, 'thumbup_time': 1th_time}), json.dumps({'thumbup_user': 2nd_user, 'thumbup_time': 2nd_time}), ...]}。
            thumbup_item = ThumbupItem(
                user_id = None,
                post_id = None,
                thumbup_list = None
            )
            thumbup_item['user_id'] = forward_item['user_id']
            thumbup_item['post_id'] = forward_item['post_id']
            thumbup_item['thumbup_list'] = []

            start_thumbup_url = 'http://weibo.cn' + div_selector.xpath('span[3]/a/@href').extract_first()
            yield scrapy.Request(
                url = start_thumbup_url,
                meta = {'item': thumbup_item},
                callback = self.parse_thumbup
            )

    # 爬取某条微博的所有点赞信息， 爬取结束后返回。
    def parse_thumbup(self, response):
        thumbup_item = response.meta['item']

        for div_selector in response.xpath('/html/body/div[@class="c"]'):
            if div_selector.xpath('span[@class="ct"]'):
                thumbup_user = div_selector.xpath('a/text()').extract_first()
                thumbup_time = re.split('来自', div_selector.xpath('span[@class="ct"]/text()').extract_first())[0].strip()

                thumbup_item['thumbup_list'].append(json.dumps({
                    'thumbup_user': thumbup_user,
                    'thumbup_time': thumbup_time
                }))

        # 如果后面还存在着其他点赞， 则生成下一页点赞的 Request 对象。
        if response.xpath('//div[@class="pa" and @id="pagelist"]') \
                and response.xpath('//div[@class="pa" and @id="pagelist"]/form/div/a[1]/text()').extract_first() == '下页':
            next_url = 'http://weibo.cn' \
                       + response.xpath('//div[@class="pa" and @id="pagelist"]/form/div/a[1]/@href').extract_first()
            yield scrapy.Request(
                url = next_url,
                meta = {'item': thumbup_item},
                callback = self.parse_thumbup
            )
        # 否则， 返回该条微博的所有点赞信息。
        else:
            yield thumbup_item