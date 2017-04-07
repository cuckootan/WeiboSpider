# -*- coding: utf-8 -*-

# Scrapy settings for WeiboSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'WeiboSpider'

SPIDER_MODULES = ['WeiboSpider.spiders']
NEWSPIDER_MODULE = 'WeiboSpider.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:47.0) Gecko/20100101 Firefox/47.0'

# Obey robots.txt rules
#ROBOTSTXT_OBEY = True

CONCURRENT_ITEMS = 20

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 2

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 8
DOWNLOAD_TIMEOUT = 300
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 2
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#    'Accept-Language': 'en-US,en;q=0.5',
# }

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'WeiboSpider.middlewares.MyCustomSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
# Use my own cookie middleware.
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': None,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'WeiboSpider.middlewares.CustomCookiesMiddleware': 401,
    'WeiboSpider.middlewares.CustomUserAgentsMiddleware': 402,
    'WeiboSpider.middlewares.CustomHeadersMiddleware': 403
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
# Use my own item pipline.
ITEM_PIPELINES = {
    'WeiboSpider.pipelines.WeibospiderPipeline': 300
}

LOG_LEVEL = 'INFO'

# Default queue is LIFO, here uses FIFO.
DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 2
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 10
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = True

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

REQUEST_CUSTOM_USER_AGENT_LIST = [
    {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"
    }
]

REQUEST_CUSTOM_HEADER_LIST = [
    {
        "Host": "weibo.cn",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
]

# If set to True, WEIBO_LOGIN_INFO_LIST will be ignored.
CUSTOM_COOKIES = True

REQUEST_CUSTOM_COOKIE_LIST = [
    [
        {
            "name": "_T_WM",
            "value": "f64c564b868e1cf4524e03ac8e73dbf1",
            "domain": ".weibo.cn",
            "path": "/"
        },
        {
            "name": "SUB",
            "value": "_2A25141EKDeRhGeNM71AX9y7Ezj-IHXVXLH9CrDV6PUJbkdAKLUfbkW1MxbUzn6ftDpbR9LG294VmZnBBrg..",
            "domain": ".weibo.cn",
            "path": "/"
        },
        {
            "name": "gsid_CTandWM",
            "value": "4u4191d91cCxb8HotkddOlZRcdL",
            "domain": ".weibo.cn",
            "path": "/"
        },
        {
            "name": "PHPSESSID",
            "value": "12711b317a8ed457fa504f54a022e4a9",
            "domain": ".weibo.cn",
            "path": "/"
        }
    ]
]

# Your whole weibo username and password pairs.
# WEIBO_LOGIN_INFO_LIST = [('your username_1', 'your password_1'), ('your username_2', 'your password_2'), ...]

# Each name of tables can be defined here (each value of items). These keys are not changeable.
TABLE_NAME_DICT = {
    'user_info': 'user_info_table_name',
    'follow': 'follow_table_name',
    'fan': 'fan_table_name',
    'post_info': 'post_info_table_name',
    'text': 'text_table_name',
    'image': 'image_table_name',
    'comment': 'comment_table_name',
    'forward': 'forward_table_name',
    'thumbup': 'thumbup_table_name'
}

# Maximum follow pages(requests) crawled for per user.
# It must be a positive number or None. None implys that crawling all follow pages.
MAX_FOLLOW_PAGES_PER_USER = 30
# Maximum fan pages(requests) crawled for per user.
# It must be a positive number or None. None implys that crawling all fan pages.
MAX_FAN_PAGES_PER_USER = 30
# Maximum post pages(requests) crawled for per user. And the maximum texts crawled in per post also equal to it.
# It must be a positive number or None. None implys that crawling all post pages.
MAX_POST_PAGES_PER_USER = 50
# Maximum image pages(requests) crawled in per post.
# It must be a positive number or None. None implys that crawling all image pages.
MAX_IMAGE_PAGES_PER_POST = None
# Maximum comment pages(requests) crawled in per post.
# It must be a positive number or None. None implys that crawling all comment pages.
MAX_COMMENT_PAGES_PER_POST = 30
# Maximum forward pages(requests) crawled in per post.
# It must be a positive number or None. None implys that crawling all forward pages.
MAX_FORWARD_PAGES_PER_POST = 30
# Maximum thumbup pages(requests) crawled in per post.
# It must be a positive number or None. None implys that crawling all thumbup pages.
MAX_THUMBUP_PAGES_PER_POST = 30

# Your postgresql username.
POSTGRESQL_USERNAME = 'your postgresql username'
# Your postgresql password.
POSTGRESQL_PASSWORD = 'your postgresql password'
# Your postgresql databaes.
POSTGRESQL_DATABASE = 'your postgresql database name'

# The IDs of users you want to crawl.
CRAWLED_WEIBO_ID_LIST = ['123456789', '246812345', ...]

# Email notification.
MAIL_ENABLED = False
MAIL_FROM = 'your email'
MAIL_HOST = 'your email smtp server host'
# Your email smtp server port
MAIL_PORT = 587
MAIL_USER = 'your email'
MAIL_PASS = 'your email password'
# YOur email smtp server port type
MAIL_TLS = True
MAIL_SSL = False
TO_ADDR = ['send to where']
