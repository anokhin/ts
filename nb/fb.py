"""
Facebook Graph API implementation stub
https://developers.facebook.com/docs/graph-api/reference/
"""

import datetime

from api import Api

__author__ = 'Nikolay Anokhin'


class FbApi(Api):

	endpoint = "https://graph.facebook.com/{method}"

	def get_node(self, node, **params):
		return self.call(node, params=params)

	def get_edge(self, node, edge, **params):
		return self.call("{node}/{edge}".format(node=node, edge=edge), params=params)

	def get_friend_ids(self, uid):
		json = self.get_edge(uid, "friends", uid=uid)
		for friend in json.get("data", []):
			yield friend["id"]

	def get_user(self, uid):
		json = self.get_node(uid, fields="gender,relationship_status,languages")
		json1 = self.get_edge(uid, "likes", uid = uid)
		list_like = [each.get("category") for each in json1["data"]]
		list_lang = []
		if json.get("languages") != None:
			list_lang = [each.get("name") for each in json.get("languages")]
		return (json.get("gender"), json.get("relationship_status"),"%s" % list_lang, "%s" % list_like)

		
def main():
	token = "CAACEdEose0cBAKxPlauyCQCZBl0DZAfP8zMvCrCgK6OABENeZAfoPK823XAJ0WERz3fZAteRUpEmokOEtgFi2O1VFSvpgDElGolzt0zzc1AuBfA7XtHS3L5E4XUBqWZACmyO5LjmMVhqbDrnUtn7R5XmGHHBFEBh3H7UHBg2nz4K8hV7DliFwKhNMIRPHeUuoC8nXd4jhkwZDZD"
	api = FbApi(token)
	f = open('info.txt', 'w+')
	for uid in api.get_friend_ids("me"):
		u = api.get_user(uid)
		f.write (u"\t".join([unicode(each) for each in u]) + u'\n')
	f.close()

if __name__ == "__main__":
	main()
