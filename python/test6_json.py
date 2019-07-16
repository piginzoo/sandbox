import json
conf = json.load(open("config.json"))
print conf
for i in conf:
	print i