#! /usr/bin/python
# -*- coding: UTF-8 -*-

import facebook
import urllib2
import codecs

print "You need API token: get one here: https://developers.facebook.com/tools/explorer"
USER_ACCESS_TOKEN= raw_input("Your API key: ")

graph = facebook.GraphAPI(USER_ACCESS_TOKEN)

def message_query_factory(thread_id, count):
	queries = []
	if count > 50:
		for min_limit in range(0, count - count % 50, 50):
			queries.append("SELECT author_id, message_id, body, created_time FROM message WHERE thread_id=%s LIMIT %s,%s" % (thread_id, min_limit, min_limit + 50))
		queries.append("SELECT author_id, message_id, body, created_time FROM message WHERE thread_id=%s LIMIT %s,%s" % (thread_id, min_limit + 50, count))
	else:
		queries.append("SELECT author_id, message_id, body, created_time FROM message WHERE thread_id=%s LIMIT %s,%s" % (thread_id, 0, count))
	return queries

def fql(query):
	try:
		return graph.fql(query)
	except urllib2.URLError:
		print "restarted"
		return fql(query)
	
	
def get_object(uid):
	try:
		return graph.get_object(uid)
	except urllib2.URLError:
		print "restarted"
		return get_object(uid)

recipients = {}

def recipient(uid):
	if not recipients.has_key(uid):
		print "resolving", uid
		try:
			rec = get_object(str(uid))
			if rec.has_key("username"):
				recipients[uid] = rec["username"]
			else:
				recipients[uid] = str(uid)
		except:
			recipients[uid] = str(uid)
	return recipients[uid]



if __name__ == "__main__":
	threads = fql("SELECT thread_id, recipients, message_count FROM thread WHERE folder_id=0")

	for thread in threads:
		queries = message_query_factory(thread["thread_id"], thread["message_count"])
		thread["messages"] = []
		for n, query in enumerate(queries):
			print "%s/%s: %s" %(n+1, len(queries), query)
			thread["messages"] += fql(query)

	for thread in threads:
		if len(thread["recipients"]) < 15:
			recp = ",".join([recipient(uid) for uid in thread["recipients"]])
		else:
			recp = ",".join([str(uid) for uid in thread["recipients"]])
		print recp
		data = u""
		data += recp
		for message in thread["messages"]:
			print recipient(message["author_id"]) + ": " + message["body"]
			data += recipient(message["author_id"]) + ": " + message["body"] + "\n"
		recp = recp if not len(recp) > 40 else recp[:30]
		with codecs.open("logs/"+recp+".txt", mode="w", encoding='utf-8') as ffile:
			ffile.write(data)

