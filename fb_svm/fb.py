import datetime
import random
import argparse

from api import Api

# better use input file with token instead of this constant
token = "CAACEdEose0cBAKkmFOuZAy4VCrWC3ceZA2BPzkUw3b9BuRsu4n0DyM1GxDCzOHBPYVKpEFjWGZC6YSercAsXwE88PoTsHrpjfRpvofazYuaZCFXFtUg99AH0SjoGZA20Mk5bR9qHuz4f0SGPmhBZBrSVlwt6crcYle3uIkD473mm4MrMFpfnV6kQLTAmM4NjxPM411dg2ZC1wZDZD" 

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

	def get_user_fields(self, uid):
		json = self.get_node(uid, fields="gender,favorite_athletes,favorite_teams,inspirational_people")
		return [json.get('gender'),
				len(json.get("favorite_athletes", [])), 
				len(json.get("favorite_teams", [])), 
				len(json.get("inspirational_people", []))]
		
	def get_user_edge(self, uid, edge):
		json = self.get_edge(uid, edge, uid=uid)
		return len(json.get("data", []))


def parse_args():
	parser = argparse.ArgumentParser(description = 'FB features getter')
	parser.add_argument('-outfile', metavar='OUT', type=str, default="fb_data", help='output file for downloaded data')
	parser.add_argument('-token', metavar='T', type=str, default=token, help='file with FB token')
	
	return parser.parse_args()
		
		
def main():
	args = parse_args()
	print args
	api = FbApi(args.token)
	f = open(args.outfile, 'w+') 
	f.write(u"#columns: gender,favorite_athletes,favorite_teams,inspirational_people,albums,books,movies,groups,statuses\n")
	for uid in api.get_friend_ids("me"):
		features = api.get_user_fields(uid)
		features.append(api.get_user_edge(uid, "albums"))
		features.append(api.get_user_edge(uid, "books"))
		features.append(api.get_user_edge(uid, "movies"))
		features.append(api.get_user_edge(uid, "groups"))
		features.append(api.get_user_edge(uid, "statuses"))
		f.write(u"\t".join([unicode(elem) for elem in features]).encode('utf8') + u'\n')
	f.close()

if __name__ == "__main__":
	main()
