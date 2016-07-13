#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Jason'

import requests, base64, urllib.parse, re, json, time, binascii, rsa



class Cookies(object):
    def __init__(self, raw_username, raw_password):
        self.raw_username = raw_username
        self.raw_password = raw_password

        self.username = None
        self.password = None
        self.pre_login_data = None

    def get_cookie(self):
        self.get_username()
        self.get_prelogin_data()
        self.get_password()

        return self.login()

    def get_username(self):
        self.username = base64.b64encode(urllib.parse.quote(self.raw_username).encode("utf-8"))

    def get_prelogin_data(self):
        tm = int(time.time() * 1000)
        url = 'https://login.sina.com.cn/sso/prelogin.php?entry=account&callback=sinaSSOController.preloginCallBack&su={0:s}&rsakt=mod&client=ssologin.js(v1.4.15)&_={1:d}'.format(
            self.username.decode('utf-8'), tm)
        # print(url)

        res = requests.get(url).text
        # print(res)
        json_str = re.split(r'sinaSSOController.preloginCallBack\(|\)', res)[1]
        temp_dict = json.loads(json_str)

        servertime = str(temp_dict['servertime'])
        nonce = temp_dict['nonce']
        pubkey = temp_dict['pubkey']
        rsakv = temp_dict['rsakv']
        # print('servertime: %s\nnonce: %s\npubkey: %s\nrsakv: %s' %(servertime, nonce, pubkey, rsakv))

        self.pre_login_data = (servertime, nonce, pubkey, rsakv)

    def get_password(self):
        # 创建公钥。
        key = rsa.PublicKey(int(self.pre_login_data[2], 16), 65537)
        # 先对 message 加密，然后将结果的每一个字节转换为一个十六进制数。
        message = ('\t'.join([str(self.pre_login_data[0]), self.pre_login_data[1]]) + '\n' + self.raw_password).encode('utf-8')
        # print(message)

        self.password = binascii.b2a_hex(rsa.encrypt(message, key))
        # print(self.password)

    def login(self):
        tm = int(time.time() * 1000)
        url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)&_={0:d}'.format(tm)

        login_data = {
            'entry': b'sso',
            'gateway': b'1',
            'from': b'',
            'savestate': b'30',
            'useticket': b'0',
            'pagerefer': b'',
            'vsnf': b'1',
            'su': self.username,
            'service': b'sso',
            'servertime': self.pre_login_data[0].encode('utf-8'),
            'nonce': self.pre_login_data[1].encode('utf-8'),
            'pwencode': b'rsa2',
            'rsakv': self.pre_login_data[3].encode('utf-8'),
            'sp': self.password,
            'sr': b'1280*800',
            'encoding': b'UTF-8',
            'cdult': b'3',
            'domain': b'sina.com.cn',
            'prelt': b'97',
            'returntype': b'TEXT'
        }

        session = requests.Session()
        res = session.post(url = url, data = login_data)
        # print(res.text)

        info = json.loads(res.content.decode('utf-8'))

        if info['retcode'] == '0':
            print('Get Cookie Success! (Account: %s)' % self.raw_username)
            return session.cookies.get_dict()
        else:
            raise RuntimeError('Login Failed...Reason:{0:s}'.format(info['reason']))
