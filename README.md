# 新浪微博爬虫（单机版）

---

## 1 简介

该程序用于爬取新浪微博的数据，主要用于学术研究。具体数据包括：

-   发布微博的作者的个人信息，包括用户ID，昵称，性别，地区；
-   作者的所有关注的人；
-   作者的所有粉丝；
-   作者发布的所有微博的微博ID，发布时间；
-   每条微博的文字；
-   每条微博的所有图片；
-   每条微博的所有评论者的昵称，评论的文字，以及评论的时间；
-   每条微博的所有转发者的昵称，以及转发的时间；
-   每条微博的所有点赞者的昵称，以及点赞的时间。

另外，该爬虫还支持以下功能：

-   支持多账号爬虫。理论上，账号越多，被 ban 的几率越小；
-   支持多 user-agent 轮流使用，目的在于减小被 ban 的几率；
-   用数据库存储，爬取结束后再从数据库导出，这样方便且高效；
-   爬取结束时会自动发送邮件进行通知；

---

## 2 依赖环境

在 Linux, Mac OSX 下测试通过（Windows 没有测试，应该是可以的）。下面以 Ubuntu 为例搭建环境。

-   Python 3.5+

    `sudo apt-get install python3-dev`

    `sudo apt-get install python3-pip`
-   PostgreSQL

    `sudo apt-get install postgresql`
-   Python下的 scrapy包，requests包，rsa包，PostgreSQL 在 Python3 下的驱动 psycopg2

    `sudo python3 -m pip install -U requests`

    `sudo python3 -m pip install -U rsa`

    `sudo apt-get install libxml2-dev libxslt1-dev libffi-dev libssl-dev`

    `sudo python3 -m pip install -U scrapy`

    `sudo apt-get install libpq-dev`

    `sudo python3 -m pip install -U psycopg2`
-   配置数据库

    建立登录账号及数据库：

    ```Shell
        sudo -u postgres psql

        # username 为登录用户名，password　为该用户的密码.
        CREATE USER username WITH ENCRYPTED PASSWORD 'password';
        # databse_name 为数据库名，username 为数据库的拥有者.
        CREATE DATABASE database_name OWNER username;
        # 之后退出.
    ```

    打开权限配置文件 **/etc/postgresql/9.5/main/pg\_hba.conf**，找到 **# IPv4 local connections**，在后面添加：

    ```Shell
        # username 为登录用户名.
        host database_name username 网段 md5
    ```

    比如，**host weibo hello 114.212.0.0/16 md5**　表示这个网段内的所有主机可以通过登录 hello 账号来访问数据库 weibo。

    打开连接配置文件 **/etc/postgresql/9.5/main/postgresql.conf**，找到 **# listen\_address = 'localhost'**，取消注释，并将其设置为：

    ```Shell
        listen_address = '*'
    ```

    配置完成后，重启服务：

    `sudo service postgresql restart`

---

## 3 安装及运行

下载到本地：

`git clone https://github.com/cuckootan/WeiboSpider.git`

然后进入项目根目录，执行如下命令即可运行（前提是要对该项目配置完成，见下面）：

`scrapy crawl weibo`

>   本项目中的 scrapy 项目名为 **weibo**。

---

## 4 配置说明

1.  选用 Pycharm 作为开发及调试工具。

    打开 **Run -> Edit Configurations**，点击左上角的 **+** 添加配置信息。

    -   将 **Script** 字段填写为 **/usr/local/bin/scrapy**；
    -   将 **Script parameters** 字段填写为 **crawl weibo**；
    -   将 **Python interpreter** 字段填写为 python3 解释器的路径；
    -   将 **Working directory** 字段填写为该项目的根目录的路径。比如：**/home/username/Project/WeiboSpider**；
    -   取消 **Add content roots to PYTHONPATH** 以及 **Add source roots to PYTHONPATH**。
2.  程序中用到的所有配置都写在了项目中的 **settings.py** 里，因此将项目下载到本地后，只需配置更改其中的相应内容即可，无序修改其他源程序。
    主要包括：

    ```Python
        # Enable or disable downloader middlewares
        # See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
        # Use my own cookie middleware.
        DOWNLOADER_MIDDLEWARES = {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': None,
            # The order of custom cookies middleware can not be bigger than 700 (the one of built-in cookies middleware).
            'WeiboSpider.middlewares.CustomCookiesMiddleware': 401,
            'WeiboSpider.middlewares.CustomUserAgentsMiddleware': 402,
            'WeiboSpider.middlewares.CustomHeadersMiddleware': 403
        }

        # Configure item pipelines
        # See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
        # Use my own item pipline.
        ITEM_PIPELINES = {
            'WeiboSpider.pipelines.WeibospiderPipeline': 300
        }

        LOG_LEVEL = 'DEBUG'

        # Default queue is LIFO, here uses FIFO.
        DEPTH_PRIORITY = 1
        SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
        SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'

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
                    "host": "weibo.cn",
                    "path": "/"
                }
            ]
        ]

        # Your whole weibo username and password pairs.
        # WEIBO_LOGIN_INFO_LIST = [('your username_1', 'your password_1'), ('your username_2', 'your password_2'), ...]

        # Each name of tables can be defined here (each value of items). These keys are not changeable.
        TABLE_NAME_DICT = {
            'user_info': 'user_info',
            'follow': 'follow',
            'fan': 'fan',
            'post': 'post',
            'text': 'text',
            'image': 'image',
            'comment': 'comment',
            'forward': 'forward',
            'thumbup': 'thumbup'
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
    ```

    其中，各个表对应的结构为：

    -   user\_info 对应表的结构为： **(user\_id varchar(20) PRIMARY KEY NOT NULL, user\_name text NOT NULL, gender varchar(5) NOT NULL, district text NOT NULL)**
    -   follow 对应表的结构为： **(user\_id varchar(20) PRIMARY KEY NOT NULL, follow\_list text[] NOT NULL)**
    -   fan 对应表的结构为： **(user\_id varchar(20) PRIMARY KEY NOT NULL, fan\_list text[] NOT NULL)**
    -   post 对应表的结构为： **(user\_id varchar(20) PRIMARY KEY NOT NULL, post\_list json NOT NULL)**
    -   text 对应表的结构为： **(user\_id varchar(20) NOT NULL, post\_id varchar(20) NOT NULL, text text NOT NULL, PRIMARY KEY(user\_id, post\_id))**
    -   image 对应表的结构为： **(user\_id varchar(20) NOT NULL, post\_id varchar(20) NOT NULL, image\_list text[] NOT NULL, PRIMARY KEY(user\_id, post\_id))**
    -   comment 对应表的结构为： **(user\_id varchar(20) NOT NULL, post\_id varchar(20) NOT NULL, comment\_list json NOT NULL,PRIMARY KEY(user\_id, post\_id))**
    -   forward 对应表的结构为： **(user\_id varchar(20) NOT NULL, post\_id varchar(20) NOT NULL, forward\_list json NOT NULL, PRIMARY KEY(user\_id, post\_id))**
    -   thumbup 对应表的结构为： **(user\_id varchar(20) NOT NULL, post\_id varchar(20) NOT NULL, thumbup\_list json NOT NULL, PRIMARY KEY(user\_id, post\_id))**

    还有一些其他配置项，详见 **settings\.py**。

---

## 5 表的导出

进入数据库，对每个表执行如下命令：

`\copy table_name TO $ABSOLUTE_PATH`

其中，**$ABSOLUTE\_PATH** 为每个表对应输出文件的 **绝对路径**。

对于表中 json 类型的字段，在输出到文件后用 Python3 中的 json 包进行处理即可。

