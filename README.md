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

---

## 2 依赖环境

在 Linux, Mac OSX 下测试通过（Windows 没有测试，应该是可以的）。下面以 Ubuntu 为例搭建环境。

-   Python 3.5+

    `sudo apt-get install python3-dev`

    `sudo apt-get install python3-pip`
-   PostgreSQL

    `sudo apt-get install postgresql`
-   Python下的 scrapy包，requests包，rsa包，PostgreSQL 在python3 下的驱动 psycopg2

    `sudo python3 -m pip install requests`

    `sudo python3 -m pip install rsa`

    `sudo apt-get install libxml2-dev libxslt1-dev libffi-dev libssl-dev`

    `sudo python3 -m pip install scrapy`
    
    `sudo apt-get install libpq-dev`

    `sudo python3 -m pip install psycopg2`

---

## 3 安装及运行

下载到本地：

`git clone https://github.com/cuckootan/WeiboSpider.git`

然后进入项目根目录，执行如下命令即可运行（前提是要对该项目配置完成，见下面）：

`scrapy crawl weibo`

---

## 4 配置说明

-   选用 Pycharm 作为开发及调试工具；
-   配置 PostgreSQL 并建立数据库。由于在本项目中使用的是无密码的 postgresql 用户及数据库，因此在本项目中一定要保证有这么一个用户。
-   程序中用到的所有配置都写在了项目中的 settings.py 里，因此将项目下载到本地后，只需配置更改其中的相应内容即可，无序修改其他源程序。
    主要包括：

    ```python
        # Your weibo username.
        WEIBO_USERNAME = 'your username'
        # Your weibo password.
        WEIBO_PASSWORD = 'your password'
        # Each name of tables can be defined here (each value of items).
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

        # Your postgresql username (that must be connected without password).
        POSTGRESQL_USERNAME = 'your postgresql username'
        # Your postgresql databaes.
        POSTGRESQL_DATABASE = 'your database name'

        # The user id you want to crawl.
        CRAWLED_WEIBO_ID_LIST = ['123456789', '246812345']
    ```
    其中，各个表的所有列的字段及数据类型分别为（它们不能被改变，表名可以改变）：
    
    -   user_info. (user_id varchar(20), user_name text, gender varchar(5), district text)
    -   follow. (user_id varchar(20), follow_list text[])
    -   fan. (user_id varchar(20), fan_list text[])
    -   post_info. (user_id varchar(20), post_id varchar(20), publist_time text)
    -   text. (user_id varchar(20), post_id varchar(20), text text)
    -   image. (user_id varchar(20), post_id varchar(20), image_list text[])
    -   comment. (user_id varchar(20), post_id varchar(20), comment_list json)
    -   forward. (user_id varchar(20), post_id varchar(20), forward_list json)
    -   thumbup. (user_id varchar(20), post_id varchar(20), thumbup_list json)

    还有一些其他配置项，详见 settings.py。
