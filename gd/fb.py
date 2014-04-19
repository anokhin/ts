"""
Facebook Graph API implementation stub
https://developers.facebook.com/docs/graph-api/reference/
"""

import datetime
import user
import random

from api import Api


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
        json = self.get_node(uid, fields="id,birthday,first_name,gender,last_name,languages")
        return self.json_to_user(json)

    def get_user_edge(self, uid, edge):
        json = self.get_edge(uid, edge, uid=uid)
        return "\t%d" % len(json.get("data", []))
          
    @staticmethod
    def json_to_user(json):
        u = user.User(json['id'], json['first_name'], json['last_name'])
        u.sex = json.get('gender')
        u.set_age(FbApi.parse_birth_date(json.get('birthday')))
        
        languages = []
        lang = json.get('languages')
        if lang is not None:
          u.languages = len(lang)
         
        return u

    @staticmethod
    def parse_birth_date(birth_date_str):
        if birth_date_str:
            parts = birth_date_str.split('/')
            if len(parts) == 3:
                return datetime.date(int(parts[2]), int(parts[0]), int(parts[1]))


def main():
    token = "CAACEdEose0cBANZAtq3fPQnR9cGgVVZAQPAeQPZCtd3BNe0l15cmZCKwyPhd3cukADTZCs4Mm4gtkFyHfcw3IqblQNQh0yuF7MeNaspZB0OfngIOw1noG9BmDCFkGV9WuHzmwZBIi8gTgzFVFZBQ70ijoO5UWlO3m5nJK6em2JZAgsrGZAys0OQJ2lYt4mJiXbwhyp1xTlj9L2WQZDZD"
    api = FbApi(token)
    
    f = open('/path/to/outfile.txt', 'w+') #path to outfile
    for uid in api.get_friend_ids("me"):
        u = api.get_user(uid)
        f.write(u.to_tsv().encode('utf8'))
        f.write(api.get_user_edge(uid,"likes"))
        f.write(api.get_user_edge(uid,"groups"))
        f.write(api.get_user_edge(uid,"statuses"))
        f.write(api.get_user_edge(uid,"albums"))
        f.write(u'\n')


    f.close()


if __name__ == "__main__":
    main()
