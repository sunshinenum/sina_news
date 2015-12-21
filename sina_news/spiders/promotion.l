start from an index page

don't request the same url

only request urls that contain "vt=1"

make all requests in the queue

add lock for mysql connection

change log level to info 

settings:
			CONCURRENT_REQUESTS = 64
			CONCURRENT_REQUESTS_PER_DOMAIN=64
			