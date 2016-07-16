#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Jason'

from . import cookies
import random



class CookiesMiddleware(object):
    def __init__(self, weibo_login_info_list):
        self.cookie_list = []

        for info_item in weibo_login_info_list:
            self.cookie_list.append(cookies.Cookies(info_item[0], info_item[1]).get_cookie())

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            weibo_login_info_list = crawler.settings.get('WEIBO_LOGIN_INFO_LIST')
        )

    def process_request(self, request, spider):
        request.cookies = random.choice(self.cookie_list)

class UserAgentsMiddleware(object):
    def __init__(self):
        self.user_agent_list = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:47.0) Gecko/20100101 Firefox/47.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'
        ]

    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(self.user_agent_list)
