#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Jason'

from . import cookies

import random



class CustomCookiesMiddleware(object):
    def __init__(self, settings):
        custom_cookies = settings.get('CUSTOM_COOKIES')

        if custom_cookies:
            self.cookie_list = settings.get('REQUEST_CUSTOM_COOKIE_LIST')
        else:
            weibo_login_info_list = settings.get('WEIBO_LOGIN_INFO_LIST')
            self.cookie_list = []

            for info_item in weibo_login_info_list:
                self.cookie_list.append(cookies.Cookies(info_item[0], info_item[1]).get_cookie())

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            settings = crawler.settings
        )

    def process_request(self, request, spider):
        request.cookies = random.choice(self.cookie_list)

class CustomHeadersMiddleware(object):
    def __init__(self, settings):
        self.header_list = settings.get('REQUEST_CUSTOM_HEADER_LIST')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            settings = crawler.settings
        )

    def process_request(self, request, spider):
        headers = random.choice(self.header_list)

        for key, value in headers.items():
            request.headers[key] = value

class CustomUserAgentsMiddleware(object):
    def __init__(self, settings):
        self.user_agent_list = settings.get('REQUEST_CUSTOM_USER_AGENT_LIST')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            settings=crawler.settings
        )

    def process_request(self, request, spider):
        request.headers[b'User-Agent'] = random.choice(self.user_agent_list)
