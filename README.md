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
-   Python下的 scrapy包，requests包，rsa包，PostgreSQL 在python3 下的驱动 psycopg2

    `sudo python3 -m pip install --upgrade requests`

    `sudo python3 -m pip install --upgrade rsa`

    `sudo apt-get install libxml2-dev libxslt1-dev libffi-dev libssl-dev`

    `sudo python3 -m pip install --upgrade scrapy`
    
    `sudo apt-get install libpq-dev`

    `sudo python3 -m pip install --upgrade psycopg2`

---

## 3 安装及运行

下载到本地：

`git clone https://github.com/cuckootan/WeiboSpider.git`

然后进入项目根目录，执行如下命令即可运行（前提是要对该项目配置完成，见下面）：

`scrapy crawl weibo`

>   本项目中的 scrapy 项目名为 **weibo**。

---

## 4 配置说明

1.  选用 Pycharm 作为开发及调试工具；
    
    打开 **Run -> Edit Configurations**，点击左上角的 **+** 添加配置信息。
    
    -   将 **Script** 字段填写为 **/usr/local/bin/scrapy**；
    -   将 **Script parameters** 字段填写为 **crawl weibo**；
    -   将 **Python interpreter** 字段填写为 python3 解释器的路径；
    -   将 **Working directory** 字段填写为该项目的根目录的路径。比如：**/home/username/Project/WeiboSpider**；
    -   取消 **Add content roots to PYTHONPATH** 以及 **Add source roots to PYTHONPATH**。
2.   配置 PostgreSQL 并建立数据库。打开 **/etc/postgresql/9.5/main/pg_hba.conf**，添加如下字段到更改用户权限的相应位置。
    
    **local    all    your_username    trust**
    
    或者
    
    **local    all    your_username    md5**
3.   程序中用到的所有配置都写在了项目中的 **settings.py** 里，因此将项目下载到本地后，只需配置更改其中的相应内容即可，无序修改其他源程序。
    主要包括：

    ```python
        # Your whole weibo username and password pairs.
        WEIBO_LOGIN_INFO_LIST = [('your username_1', 'your password_1'), ('your username_2', 'your password_2'), ...]
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

        # Your postgresql username.
        POSTGRESQL_USERNAME = 'your postgresql username'
        # Your postgresql password.
        POSTGRESQL_PASSWORD = 'your postgresql password'
        # Your postgresql databaes.
        POSTGRESQL_DATABASE = 'your database name'

        # The IDs of users you want to crawl.
        CRAWLED_WEIBO_ID_LIST = ['123456789', '246812345', ...]
    ```
    其中，各个表的所有列的字段及数据类型分别为（它们不能被改变，表名可以改变）：
    
    -   user_info 对应表的结构为： **(user_id varchar(20), user_name text, gender varchar(5), district text)**
    -   follow 对应表的结构为： **(user_id varchar(20), follow_list text[])**
    -   fan 对应表的结构为： **(user_id varchar(20), fan_list text[])**
    -   post_info 对应表的结构为： **(user_id varchar(20), post_id varchar(20), publist_time text)**
    -   text 对应表的结构为： **(user_id varchar(20), post_id varchar(20), text text)**
    -   image 对应表的结构为： **(user_id varchar(20), post_id varchar(20), image_list text[])**
    -   comment 对应表的结构为： **(user_id varchar(20), post_id varchar(20), comment_list json)**
    -   forward 对应表的结构为： **(user_id varchar(20), post_id varchar(20), forward_list json)**
    -   thumbup 对应表的结构为： **(user_id varchar(20), post_id varchar(20), thumbup_list json)**

    还有一些其他配置项，详见 settings.py。

## 5 数据的导出

进入 **setting.py** 中指定的数据库，对每个表执行如下命令：

`\copy table_name TO $ABSOLUTE_PATH`

其中，**$ABSOLUTE_PATH** 为每个表对应输出文件的 **绝对路径**。

对于表中 json 类型的字段，在输出到文件后用 python3 中的 json 包进行处理即可。

## TODO

-   添加用于实时查看爬虫信息的图形化界面（用 Graphite）；
-   添加代理，减小被 ban 的几率。
