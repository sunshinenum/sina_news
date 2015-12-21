import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
import MySQLdb
import Queue
import threading
from scrapy import log
import time
import pickle
import os

class SinaNewsSpider(scrapy.spiders.Spider):
	
	# number of news inserted into database
	s_number_news_got = 0

	#BFS queue
	g_queue_urls = Queue.Queue(100000)
	g_container_urls = {""}
	lock_queue = threading.RLock()
	lock_container = threading.RLock()

	name = "sina_news"
	allowed_domains = ["sina.cn"]
	start_urls = (
		"http://news.sina.cn/?vt=1&sa=t124d1712309v84",
		# ,"http://news.sina.cn/index1.d.html?vt=1"
		# ,"http://news.sina.cn/?sa=t124d8889597v84&vt=1"
		# ,"http://mil.sina.cn/?vt=1"
		# ,"http://news.sina.cn/roll.d.html?vt=1"
		# ,"http://sina.cn/?vt=1"
		# ,"http://news.sina.cn/gn/2015-12-13/detail-ifxmpxnx5062324.d.html"
		# ,"http://news.sina.cn/?vt=4"
		# ,"http://news.sina.cn/sh/2015-12-13/detail-ifxmpnqi6398999.d.html"
		# ,"http://news.sina.cn/guide.d.html?r=4218"
		# ,"http://house.sina.cn/touch/index/?source_ext=sina&source=m_sina_hqdh4"
	)

	lock = threading.RLock()

	conn=MySQLdb.connect(user='root', passwd='1993', db='web_pages')
	conn.autocommit(1)
	conn.set_character_set('utf8')
	cursor = conn.cursor()
	cursor.execute('SET NAMES utf8;')
	cursor.execute('SET CHARACTER SET utf8;')
	cursor.execute('SET character_set_connection=utf8;')

	# for restore: restore from file queue
	# fin_queue = open("queue","w+")
	# if os.path.getsize("queue") != 0:
	# 	g_queue_urls = pickle.load(fin_queue)
	# fin_queue.close()
	# fin_container = open("container","w+")
	# if os.path.getsize("container") != 0:
	# 	g_container_urls = pickle.load(fin_container)
	# fin_container.close()

	def parse(self, response):

		title_arr = response.xpath("/html/head/title/text()").extract()
		title = ""
		for i in title_arr:
			title = title + i

		content_arr = response.xpath("//div/text()").extract()
		content = ""
		for i in content_arr:
			if len(i) > 50:
				content = content + i
		# print content

		# put data out to file	
		# fo = open("data.txt","a")
		# fo.write("\r\n")
		# fo.write(response.url)
		# fo.write(title.encode('utf-8'))
		# fo.write(content.encode('utf-8'))
		# fo.close()

		# put data into an dictionary
		# item = {}
		# item['title'] = title
		# item['title_hash'] = hash(title)
		# item['content'] = content
		# item['url'] = response.url
		# return item

		self.store_data_into_mysql(title, hash(title), content, response.url)

		# set the allowed domains in link
		ln_extractor = LinkExtractor(allow_domains=("news.sina.cn"), allow = (".*vt=1.*"))
		# get the links from the response
		links = ln_extractor.extract_links(response)
		urls = []
		items = []

		for i in links:
			urls.append(i.url)
			# all the not visited urls are put into container and queue.
			if i.url not in self.g_container_urls:
				self.g_queue_urls.put(i.url)
				self.g_container_urls.add(i.url)
		
		# for restore: save the queue per 10s 
		# self.lock_queue.acquire()
		# self.lock_container.acquire()
		# if time.localtime().tm_sec%10 == 0:
		# 	fin_queue = open("queue", "w+");
		# 	pickle.dump(self.g_queue_urls, fin_queue)
		# 	fin_container = open("container", "w+")
		# 	pickle.dump(self.g_container_urls, fin_container)
		# 	fin_container.close()
		# 	fin_queue.close()
		# self.lock_queue.release()
		# self.lock_container.release()

		# make all the request in the queue
		for j in range(self.g_queue_urls.qsize()):
			items.append(self.make_requests_from_url(self.g_queue_urls.get()))

		return items
	
	def store_data_into_mysql(self, title, title_hash, content, url):

	    # Primary key is title_hash

	    # Is id exist ?
		IS_EXIST = 0

		SELCT_IF_EXIST = "SELECT * FROM pages WHERE page_id = '%d';"
		INSERT_INTO_DB_VALUES = "INSERT INTO pages VALUES('%d', '%s' , '%s', '%s');"

		self.lock.acquire()
		rows = self.cursor.execute(SELCT_IF_EXIST % title_hash)

		if rows == 0 and len(content) > 10:
			self.cursor.execute(INSERT_INTO_DB_VALUES % (title_hash, url, title, content))
			self.s_number_news_got += 1
			log.msg(str(self.s_number_news_got)+":title:"+title+" url:"+url, level=log.INFO)
		self.lock.release()
