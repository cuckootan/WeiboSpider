#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Jason'

from . import cookies
from datetime import datetime



class CookiesMiddleware(object):
    def __init__(self, username, password):
        self.cookie = cookies.Cookies(username, password).get_cookie()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            username = crawler.settings.get('WEIBO_USERNAME'),
            password = crawler.settings.get('WEIBO_PASSWORD')
        )

    def process_request(self, request, spider):
        request.cookies = self.cookie
