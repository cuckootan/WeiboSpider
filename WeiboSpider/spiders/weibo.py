# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import CrawlSpider

from WeiboSpider.items import UserInfoItem, FollowListItem, FanListItem, \
    PostInfoItem, TextItem, ImageListItem, CommentListItem, ForwardListItem, ThumbupListItem



class WeiboSpider(CrawlSpider):
    name = 'weibo'
    allowed_domains = ['weibo.cn']

    def start_requests(self):
        print("start...")

        user_info_item = UserInfoItem()

        yield scrapy.Request(
            url = "http://weibo.cn/3592470455/info",
            meta = {"user_id": "3592470455", "item": user_info_item},
            callback = self.parse_user_info)

    def parse_user_info(self, response):
        user_info_item = response.meta["item"]

        user_info_item["user_id"] = response.meta["user_id"]

        for div_selector in response.xpath("//div[@class=\"c\"]"):
            if div_selector.xpath("text()") and div_selector.xpath("text()").extract_first()[:2] == "昵称":
                break

        user_info_item["user_name"] = div_selector.xpath("text()[1]").extract_first()[3:]
        user_info_item["gender"] = div_selector.xpath("text()[3]").extract_first()[3:]
        user_info_item["district"] = div_selector.xpath("text()[4]").extract_first()[3:]

        yield user_info_item

        follow_list_item = FollowListItem()
        fan_list_item = FanListItem()

        yield scrapy.Request(
            url = "http://weibo.cn/3592470455/follow?page=1",
            meta = {"user_name": user_info_item["user_name"], "item": follow_list_item},
            callback = self.parse_follow)
        yield scrapy.Request(
            url = "http://weibo.cn/3592470455/fans?page=1",
            meta = {"user_name": user_info_item["user_name"], "item": fan_list_item},
            callback = self.parse_fan)

        yield scrapy.Request(
            url = "http://weibo.cn/3592470455/profile?page=1",
            meta = {"user_name": user_info_item["user_name"]},
            callback = self.parse_post_info)

    def parse_follow(self, response):
        follow_list_item = response.meta["item"]

        for table_selector in response.xpath("/html/body/table"):
            follow_list_item.append(table_selector.xpath("tr/td[2]/a[1]/text()").extract_first())

        if response.xpath("//*[@id=\"pagelist\"]")\
                and response.xpath("//*[@id=\"pagelist\"]/form/div/a[1]/text()").extract_first() == "下页":
            next_url = "http://weibo.cn" + response.xpath("//*[@id=\"pagelist\"]/form/div/a[1]/@href").extract_first()
            yield scrapy.Request(
                url = next_url,
                meta = {"user": "今日重庆", "item": follow_list_item},
                callback = self.parse_follow)
        else:
            yield follow_list_item

    def parse_fan(self, response):
        fan_list_item = response.meta["item"]

        for div_selector in response.xpath("/html/body/div[@class=\"c\"]"):
            if div_selector.xpath("table"):
                break

        for table_selector in div_selector.xpath("table"):
            fan_list_item.append(table_selector.xpath("tr/td[2]/a[1]/text()").extract_first())

        if response.xpath("//*[@id=\"pagelist\"]")\
                and response.xpath("//*[@id=\"pagelist\"]/form/div/a[1]/text()").extract_first() == "下页":
            next_url = "http://weibo.cn" + response.xpath("//*[@id=\"pagelist\"]/form/div/a[1]/@href").extract_first()
            yield scrapy.Request(
                url = next_url,
                meta = {"user_name": "今日重庆", "item": fan_list_item},
                callback = self.parse_fan)
        else:
            yield fan_list_item

    def parse_post_info(self, response):
        for div_selector in response.xpath("//div[@class=\"c\"]"):
            if div_selector.xpath("@id"):
                # 转发的微博, 不爬取。
                if div_selector.xpath("div[1]/span[1]")\
                        and div_selector.xpath("div[1]/span[1]/text()").extract_first()[:2] == "转发":
                    continue

                post_info_item = PostInfoItem()
                post_info_item["user_name"] = response.meta["user_name"]
                post_info_item["post_id"] = div_selector.xpath("@id").extract_first()

                text_item = TextItem()
                text_item["user_name"] = post_info_item["user_name"]
                text_item["post_id"] = post_info_item["post_id"]
                text_item["text"] = div_selector.xpath("div[1]/span[@class=\"ctt\"]/text()").extract_first()

                # 如果存在图像。
                if div_selector.xpath("div[2]"):
                    post_info_item["publish_time"] = div_selector.xpath("div[2]/span[@class=\"ct\"]/text()").extract_first()

                    for a_selector in div_selector.xpath("div[2]/a"):
                        temp_str = a_selector.xpath("text()").extract_first()

                        if not temp_str:
                            image_start_url = a_selector.xpath("@href").extract_first()
                        elif temp_str[:2] == "转发":
                            forward_start_url = a_selector.xpath("@href").extract_first()
                        elif temp_str[:2] == "评论":
                            comment_start_url = a_selector.xpath("@href").extract_first()
                else:
                    post_info_item["publish_time"] = div_selector.xpath("div[1]/span[@class=\"ct\"]/text()").extract_first()
                    image_start_url = None

                    for a_selector in div_selector.xpath("div[1]/a"):
                        temp_str = a_selector.xpath("text()").extract_first()
                        if temp_str[:2] == "转发":
                            forward_start_url = a_selector.xpath("@href").extract_first()
                        elif temp_str[:2] == "评论":
                            comment_start_url = a_selector.xpath("@href").extract_first()

                yield post_info_item
                yield text_item

                image_list_item = ImageListItem()
                comment_list_item = CommentListItem()
                forward_list_item = ForwardListItem()
                image_list_item["user_name"] = post_info_item["user_name"]
                image_list_item["post_id"] = post_info_item["post_id"]
                image_list_item["image_list"] = []
                comment_list_item["user_name"] = post_info_item["user_name"]
                comment_list_item["post_id"] = post_info_item["post_id"]
                comment_list_item["comment_list"] = []
                forward_list_item["user_name"] = post_info_item["user_name"]
                forward_list_item["post_id"] = post_info_item["post_id"]
                forward_list_item["forward_list"] = []

                if image_start_url:
                    yield scrapy.Request(
                        url = image_start_url,
                        meta = {"item": image_list_item},
                        callback = self.parse_image)

                yield scrapy.Request(
                    url = comment_start_url,
                    meta = {"item": comment_list_item},
                    callback = self.parse_comment)

                yield scrapy.Request(
                    url = forward_start_url,
                    meta = {"item": forward_list_item},
                    callback = self.parse_forward)

        if response.xpath("//div[@class=\"pa\" and @id=\"pagelist\"]") \
                and response.xpath("//div[@class=\"pa\" and @id=\"pagelist\"]/form/div/a[1]/text()").extract_first() == "下页":
            next_url = "http://weibo.cn" \
                       + response.xpath("//div[@class=\"pa\" and @id=\"pagelist\"]/form/div/a[1]/@href").extract_first()
            yield scrapy.Request(
                url = next_url,
                meta = {"user_name": post_info_item["user_name"]},
                callback = self.parse_post_info)

    def parse_image(self, response):
        image_list_item = response.meta["item"]

        for div_selector in response.xpath("/html/body/div[@class=\"c\"]"):
            # 如果只有一张图片。
            if div_selector.xpath("img"):
                image_list_item["image_list"].append(div_selector.xpath("img/@src").extract_first())
                yield

            if div_selector.xpath("a") and div_selector.xpath("a/img"):
                break

        image_list_item["image_list"].append(div_selector.xpath("a[1]/img/@src").extract_first())

        if div_selector.xpath("div[2]/a[1]/text()").extract_first() == "下一张":
            next_url = "http://weibo.cn" + div_selector.xpath("div[2]/a[1]/@href").extract_first()
            yield scrapy.Request(
                url = next_url,
                meta = {"item": image_list_item},
                callback = self.parse_image)
        else:
            yield image_list_item

    def parse_comment(self, response):
        comment_list_item = response.meta["item"]

        for div_selector in response.xpath("/html/body/div[@class=\"c\"]"):
            if div_selector.xpath("@id") and div_selector.xpath("@id").extract_first()[0] == "C":
                comment_user = div_selector.xpath("a[1]/text()").extract_first()

                # 不抽取 @ 某人的评论。
                if div_selector.xpath("span[@class=\"ctt\"]/a"):
                    continue

                if comment_user == comment_list_item["user_name"]:
                    comment_text = div_selector.xpath("span[@class=\"ctt\"]/text()[2]").extract_first()
                else:
                    comment_text = div_selector.xpath("span[@class=\"ctt\"]/text()").extract_first()

                comment_time = div_selector.xpath("span[@class=\"ct\"]/text()").extract_first()

                comment_list_item["comment_list"].append((comment_user, comment_text, comment_time))

        if response.xpath("//div[@class=\"pa\" and @id=\"pagelist\"]") \
                and response.xpath("//div[@class=\"pa\" and @id=\"pagelist\"]/form/div/a[1]/text()").extract_first() == "下页":
            next_url = "http://weibo.cn" \
                       + response.xpath("//div[@class=\"pa\" and @id=\"pagelist\"]/form/div/a[1]/@href").extract_first()
            yield scrapy.Request(
                url = next_url,
                meta = {"item": comment_list_item},
                callback = self.parse_comment)

    def parse_forward(self, response):
        forward_list_item = response.meta["item"]

        for div_selector in response.xpath("/html/body/div[@class=\"c\"]"):
            if div_selector.xpath("span[@class=\"ct\"]"):
                forward_user = div_selector.xpath("a/text()").extract_first()
                forward_time = div_selector.xpath("span[@class=\"ct\"]/text()").extract_first()

                forward_list_item["forward_list"].append((forward_user, forward_time))

        if response.xpath("//div[@class=\"pa\" and @id=\"pagelist\"]") \
                and response.xpath("//div[@class=\"pa\" and @id=\"pagelist\"]/form/div/a[1]/text()").extract_first() == "下页":
            next_url = "http://weibo.cn" \
                       + response.xpath("//div[@class=\"pa\" and @id=\"pagelist\"]/form/div/a[1]/@href").extract_first()
            yield scrapy.Request(
                url = next_url,
                meta = {"item": forward_list_item},
                callback = self.parse_forward)

        else:
            for div_selector in response.xpath("/html/body/div"):
                if div_selector.xpath("span[@class=\"pms\"]"):
                    break

            thumbup_list_item = ThumbupListItem()
            thumbup_list_item["user_name"] = forward_list_item["user_name"]
            thumbup_list_item["post_id"] = forward_list_item["post_id"]
            thumbup_list_item["thumbup_list"] = []

            start_thumbup_url = "http://weibo.cn" + div_selector.xpath("span[3]/a/@href").extract_first()
            yield scrapy.Request(
                url = start_thumbup_url,
                meta = {"item": thumbup_list_item},
                callback = self.parse_thumbup)

    def parse_thumbup(self, response):
        thumbup_list_item = response.meta["item"]

        for div_selector in response.xpath("/html/body/div[@class=\"c\"]"):
            if div_selector.xpath("span[@class=\"ct\"]"):
                thumbup_user = div_selector.xpath("a/text()").extract_first()
                thumbup_time = div_selector.xpath("span[@class=\"ct\"]/text()").extract_first()

                thumbup_list_item["thumbup_list"].append((thumbup_user, thumbup_time))

        if response.xpath("//div[@class=\"pa\" and @id=\"pagelist\"]") \
                and response.xpath("//div[@class=\"pa\" and @id=\"pagelist\"]/form/div/a[1]/text()").extract_first() == "下页":
            next_url = "http://weibo.cn" \
                       + response.xpath("//div[@class=\"pa\" and @id=\"pagelist\"]/form/div/a[1]/@href").extract_first()
            yield scrapy.Request(
                url = next_url,
                meta = {"item": thumbup_list_item},
                callback = self.parse_thumbup)
        else:
            yield thumbup_list_item