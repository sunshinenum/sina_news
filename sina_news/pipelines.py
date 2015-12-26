
import threading
from scrapy import log
import pymongo
from scrapy.conf import settings

class SinaNewsPipeline(object):
	
	# number of news inserted into database
	s_number_news_got = 0
	
	def __init__(self):
		connection = pymongo.MongoClient(
			settings['MONGODB_SERVER'],
			settings['MONGODB_PORT']
		)
		db = connection[settings['MONGODB_DB']]
		self.collection = db[settings['MONGODB_COLLECTION']]

	def process_item(self, item, spider):
		if self.check_data(item):
			self.collection.insert(dict(item))

			self.s_number_news_got +=1
			log.msg("[+] %s stored " % self.s_number_news_got + item['title'], level=log.INFO)
		return item

	# check if the data should be put into mongo
	def check_data(self, item):
		content_tp = item['content']
		title_tp = {}
		title_tp['title_hash'] = item['title_hash']
		if len(content_tp) < 10 or self.collection.find(title_tp).count() > 0:
			return False
		return True