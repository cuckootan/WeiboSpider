#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "Jason"

from . import cookies



id_info = {"raw_username": "joeyt.firefly@outlook.com", "raw_password": "mpn6839_PIG"}
cookie = cookies.Cookies(id_info["raw_username"], id_info["raw_password"]).get_cookie()

user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:47.0) Gecko/20100101 Firefox/47.0"

class CookiesMiddleware(object):
    def process_request(self, request, spider):
        request.cookies = cookie

class UserAgentMiddleware(object):
    def process_request(self, request, spider):
        request.headers["User-Agent"] = user_agent