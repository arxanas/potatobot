from piazza_api import Piazza
import json
import sys

p = Piazza()
p.user_login()

course = p.network(sys.argv[1])

mapSave = {}

posts = course.iter_all_posts(limit=100000000000)
for post in posts:
	content = post["history"][0]["content"]
	id = post["nr"]
	print (id)
	mapSave[id] = content

with open("posts183.json","wb") as f:
	f.write(json.dumps(mapSave))
