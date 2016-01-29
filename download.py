from piazza_api import Piazza
import pprint
import json

p = Piazza()
p.user_login()

eecs183 = p.network("iiw41ofw7igeu")

mapSave={}

posts = eecs183.iter_all_posts(limit=100000000000)
for post in posts:
	# print("type ",post["status"] )

	if post["status"] != "private":
		content=post["history"][0]["content"]
		id=post["nr"]
		mapSave[id]=content

with open("eecs281jsim.json","wb") as f:
	f.write(json.dumps(mapSave))