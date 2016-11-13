# from requests import async
# import requests
import time
import grequests

# def print_content(response):
    # print response.content
# with open('/home/mythxcq/test.jpeg', 'rb') as f:
    # image_content = f.read()

# files = {'image': image_content}
# items = [grequests.post("http://localhost:8080/person_detection", files=files)]
items = []
for i in range(400):
    files = {'image': open('/home/mythxcq/test.jpeg', 'rb')}
    items.append(grequests.post("http://192.168.3.65:8080/person_detection", files=files))

r = grequests.map(items)
for res in r:
    print res.content

# r = requests.post("http://localhost:8080/person_detection", files=files)
# print r.content
