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

io_loop = tornado.ioloop.IOLoop.current()
io_loop.add_timeout(datetime.timedelta(milliseconds=interval), next_post)
io_loop.start()

# def print_content(response):
    # print response.content
# with open('/home/mythxcq/test.jpeg', 'rb') as f:
    # image_content = f.read()

# files = {'image': image_content}
# items = [grequests.post("http://localhost:8080/person_detection", files=files)]
# items = []
# for i in range(400):
    # files = {'image': open('/home/mythxcq/3.jpeg', 'rb')}
    # items.append(grequests.post("http://localhost:8080/person_detection", files=files))
    # # items.append(grequests.post("http://localhost:8080/person_detection"))

# import pdb; pdb.set_trace()  # XXX BREAKPOINT
# print 'send all post'
# r = grequests.map(items)
# pres = ''
# for res in r:
    # pres += res.content+'\t'
    # # print res.content
# print pres

# # r = requests.post("http://localhost:8080/person_detection", files=files)
# # print r.content
