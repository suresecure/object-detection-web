# from requests import async
import tornado
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
from tornado import gen, web
import datetime
# import requests
import time
import grequests

request_count = 0
response_count = 0

sleep_test_count = 0
@gen.coroutine
def sleep_test():
    global sleep_test_count
    sleep_test_count += 1
    local_test_count = sleep_test_count
    print 'sleep', local_test_count
    yield gen.sleep(2)
    print 'wake up', local_test_count

# for i in range(100):
    # sleep_test()

def handle_response(response):
    global response_count
    response_count += 1
    if response.error:
        print "Error:", response.error
    else:
        print response_count, response.body
http_client = AsyncHTTPClient(max_clients=2000)
post_request = tornado.httpclient.HTTPRequest('http://localhost:8090/person_detection', method='POST', body="xyz")
# http_client.fetch("http://www.google.com/", handle_response)

interval = 2
def next_post():
    global interval
    global request_count
    request_count +=1
    print request_count, 'request'
    http_client.fetch(post_request, handle_response)
    if request_count<200:
        io_loop.add_timeout(datetime.timedelta(milliseconds=interval), next_post)

# io_loop = tornado.ioloop.IOLoop.current()
# io_loop.add_timeout(datetime.timedelta(milliseconds=interval), next_post)
# io_loop.start()

def print_content(response):
    print response.content
with open('/home/srzn-office/helmet.jpg', 'rb') as f:
    image_content = f.read()

files = {'image': image_content}
items = [grequests.post("http://localhost:8080/person_detection", files=files)]
items = []
for i in range(100):
    files = {'image': open('/home/srzn-office/helmet.jpg', 'rb')}
    items.append(grequests.post("http://localhost:8080/person_detection", files=files))
    # items.append(grequests.post("http://localhost:8080/person_detection"))

print 'send all post'
r = grequests.map(items)
pres = ''
success = 0
failed = 0

for res in r:
    pres += res.content+'\t'
    if res.content.startswith('{\"targets\"'):
        success += 1
    else:
        failed += 1
    # print res.content
print pres
print success
print failed

# r = requests.post("http://localhost:8080/person_detection", files=files)
# print r.content
