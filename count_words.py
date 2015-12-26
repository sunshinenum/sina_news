#!/usr/bin/python
#coding=utf-8

# count the words in stored news

import pymongo
import re

# connect db
connection = pymongo.MongoClient(
	'127.0.0.1',
	27017
)
db = connection['web_pages']
collection = db['pages']

# define words
words = ['大爷','男子','大妈','女子','专家','凤姐','女孩']

# count words
print '[+] total news : %s ' % collection.find().count()
for w in words:
	c_tp = {'title':{'$regex':'.*'+w+'.*'},}
	number = collection.find(c_tp).count()
	print '[+] find word ', w, number, 'times.'
