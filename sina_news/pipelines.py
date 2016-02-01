import MySQLdb
import threading
from scrapy import log

class SinaNewsPipeline(object):
	# number of news inserted into database
	s_number_news_got = 0
	lock = threading.RLock()
	conn=MySQLdb.connect(user='root', passwd='1993', db='web_pages')
	conn.autocommit(1)
	conn.set_character_set('utf8')
	cursor = conn.cursor()
	cursor.execute('SET NAMES utf8;')
	cursor.execute('SET CHARACTER SET utf8;')
	cursor.execute('SET character_set_connection=utf8;')

	def process_item(self, item, spider):
		self.store_data_into_mysql(
			item['title'], item['title_hash'], 
			item['content'], item['url'])
		return item

	def store_data_into_mysql(self, title, title_hash, content, url):
		# Primary key is title_hash
		# Is id exist ?
		IS_EXIST = 0
		SELCT_IF_EXIST = "SELECT * FROM pages WHERE page_id = '%d';"
		INSERT_INTO_DB_VALUES = "INSERT INTO pages VALUES('%d', '%s' , '%s', '%s');"
		self.lock.acquire()
		rows = self.cursor.execute(SELCT_IF_EXIST % title_hash)
		if rows == 0 and len(content) > 10:
			self.cursor.execute(INSERT_INTO_DB_VALUES % \
				(title_hash, url, title, content))
			self.s_number_news_got += 1
			log.msg(str(self.s_number_news_got) + ":title:" \
				 + title + " url:" + url, level=log.INFO)
		self.lock.release()
