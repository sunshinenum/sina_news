#coding=utf-8
#Authored by Chen Liguo on: 2016年 02月 01日 星期一 14:22:31 CST

import MySQLdb
import os
import pickle
import Queue
import threading
import time

import scrapy
from scrapy import log
from scrapy.contrib.linkextractors import LinkExtractor
from sina_news.items import SinaNewsItem

class SinaNewsSpider(scrapy.Spider):
	#BFS queue
	g_queue_urls = Queue.Queue(100000)
	g_container_urls = {""}
	lock_queue = threading.RLock()
	lock_container = threading.RLock()

	name = "sina_news"
	allowed_domains = ["sina.cn"]
	start_urls = (
		"http://news.sina.cn/?vt=1&sa=t124d1712309v84",
	)

	def parse_page(self, response):
		title_arr = response.xpath("/html/head/title/text()").extract()
		title = ""
		for i in title_arr:
			title += i
		content_arr = response.xpath("//div/text()").extract()
		content = ""
		for i in content_arr:
			if len(i) > 50:
				content = content + i
		# put data into an dictionary
		item = SinaNewsItem()
		item['title'] = title
		item['title_hash'] = hash(title)
		item['content'] = content
		item['url'] = response.url
		return item

	def parse(self, response):
		# set the allowed domains in link
		ln_extractor = LinkExtractor(allow_domains=("news.sina.cn"),
			 allow = (".*vt=1.*"))
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
		# make all the request in the queue
		for j in range(self.g_queue_urls.qsize()):
			tp_url = self.g_queue_urls.get()
			items.append(self.make_requests_from_url(tp_url).
				replace(callback=self.parse_page))
			items.append(self.make_requests_from_url(tp_url))
		return items
