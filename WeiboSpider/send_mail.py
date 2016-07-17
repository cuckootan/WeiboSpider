#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Jason'



from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

import smtplib



def format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

smtp_server_username = 'jxtan@outlook.com'
smtp_server_password = 'xl9307_PIG'
smtp_server_host = 'smtp-mail.outlook.com'
smtp_server_port = 587
to_addr = 'jxtan@outlook.com'

msg = MIMEText('hello, send by Python...', 'plain', 'utf-8')
msg['From'] = format_addr('Python爱好者 <{0:s}>'.format(smtp_server_username))
msg['To'] = format_addr('管理员 <{0:s}>'.format(to_addr))
msg['Subject'] = Header('来自SMTP的问候……', 'utf-8').encode()

con = smtplib.SMTP(smtp_server_host, smtp_server_port)
con.starttls()
# con.set_debuglevel(1)
con.login(smtp_server_username, smtp_server_password)
con.sendmail(smtp_server_username, [to_addr], msg.as_string())
con.quit()
