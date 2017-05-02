# from requests import async
import tornado
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
from tornado import gen, web
import datetime
import mimetypes
# import requests
import time
import ast
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

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be
    uploaded as files.
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        filename = filename.encode("utf8")
        L.append('--' + BOUNDARY)
        L.append(
            'Content-Disposition: form-data; name="%s"; filename="%s"' % (
                key, filename
            )
        )
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

def handle_response(response):
    global response_count
    response_count += 1
    if response.error:
        print "Error:", response.error
    res_body = ast.literal_eval(response.body)
    if(res_body.has_key('error')):
        print res_body
    else:
        # pass
        print response_count, response.body
http_client = AsyncHTTPClient(max_clients=2000)

with open('/home/mythxcq/helmet.jpg', 'rb') as f:
    image_content = f.read()
content_type, body = encode_multipart_formdata([], [('image', 'helmet.jpg', image_content)])
headers = {"Content-Type": content_type, 'content-length': str(len(body))}
# request = HTTPRequest(url, "POST", headers=headers, body=body, validate_cert=False)
post_request = tornado.httpclient.HTTPRequest('http://192.168.1.156:8080/person_detection', method='POST', headers=headers, body=body, validate_cert=False)
# http_client.fetch("http://www.google.com/", handle_response)

interval = 6000
interval_fast = 2
fast_num = 20
def next_post():
    global interval
    global request_count
    request_count +=1
    print request_count, 'request'
    http_client.fetch(post_request, handle_response)
    if request_count%fast_num == 0:
        next_interval = interval
    else:
        next_interval = interval_fast
    if request_count<2000:
        io_loop.add_timeout(datetime.timedelta(milliseconds=next_interval), next_post)

io_loop = tornado.ioloop.IOLoop.current()
io_loop.add_timeout(datetime.timedelta(milliseconds=2), next_post)
io_loop.start()

def print_content(response):
    print response.content
with open('/home/mythxcq/helmet.jpg', 'rb') as f:
    image_content = f.read()

files = {'image': image_content}
items = [grequests.post("http://192.168.1.156:8080/person_detection", files=files)]
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
