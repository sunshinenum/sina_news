# sina_news description
	基于Scrapy的python蜘蛛，爬取新浪新闻站的所有新闻存入Mysql，采用广度优先策略，多线程爬取。

	附带Docker环境镜像。Docker 镜像下载地址：http://yunpan.cn/c3hhBUtCHKdWM  访问密码 fb3d
	This is a spider written in python. It requested links in domain 'news.sina.cn' and stored transformed data into mysql.


# preparations :
	python 2.7
	scrapy
	mysql
	mongo


# build preparations on ubuntu
	
	http://scrapy-chs.readthedocs.org/zh_CN/latest/topics/ubuntu.html#topics-ubuntu
# build preparations on other platforms
	http://scrapy-chs.readthedocs.org/zh_CN/latest/intro/install.html#intro-install-platform-notes
	
# database: mysql
	port:3306 user:root password:1993
	create database web_pages default char set utf8;
	use web_pages;
	create table pages(page_id long, url varchar(256), title varchar(256), content varchar(10240));
