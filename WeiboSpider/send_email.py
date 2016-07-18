#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Jason'

from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib

class EmailSender(object):
    def __init__(self, smtphost = None, mailfrom = None, smtpuser = None, smtppass = None, smtpport = None, smtptls = False, smtpssl = False):
        self.smtphost = smtphost
        self.mailfrom = mailfrom
        self.smtpuser = smtpuser
        self.smtppass = smtppass
        self.smtpport = smtpport
        self.smtptls = smtptls
        self.smtpssl = smtpssl

    def from_settings(self, settings):
        self.smtphost = settings.get('MAIL_HOST')
        self.mailfrom = settings.get('MAIL_FROM')
        self.smtpuser = settings.get('MAIL_USER')
        self.smtppass = settings.get('MAIL_PASS')
        self.smtpport = settings.get('MAIL_PORT')
        self.smtptls = settings.get('MAIL_TLS')
        self.smtpssl = settings.get('MAIL_SSL')

    def send(self, to_addr, subject, body, mimetype = 'plain', charset = 'utf-8'):
        msg = MIMEText(body, mimetype, charset)
        msg['From'] = self.mailfrom
        msg['To'] = to_addr
        msg['Subject'] = Header(subject, charset).encode()

        if self.smtpssl:
            con = smtplib.SMTP_SSL(self.smtphost, self.smtpport)
            con.login(self.smtpuser, self.smtppass)
            con.sendmail(self.mailfrom, [to_addr], msg.as_string())
            con.quit()
        else:
            con = smtplib.SMTP(self.smtphost, self.smtpport)
            if self.smtptls:
                con.starttls()
            con.login(self.smtpuser, self.smtppass)
            con.sendmail(self.mailfrom, [to_addr], msg.as_string())
            con.quit()