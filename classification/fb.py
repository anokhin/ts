"""
Facebook Graph API implementation stub
https://developers.facebook.com/docs/graph-api/reference/
"""

import datetime
import user

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
        json = self.get_node(uid, fields="id,birthday,first_name,gender,last_name")
        return self.json_to_user(json)

    @staticmethod
    def json_to_user(json):
        u = user.User(json['id'], json['first_name'], json['last_name'])
        u.sex = json.get('gender')
        u.set_age(FbApi.parse_birth_date(json.get('birthday')))
        return u

    @staticmethod
    def parse_birth_date(birth_date_str):
        if birth_date_str:
            parts = birth_date_str.split('/')
            if len(parts) == 3:
                return datetime.date(int(parts[2]), int(parts[0]), int(parts[1]))


def main():
    token = ""
    api = FbApi(token)
    for uid in api.get_friend_ids("me"):
        u = api.get_user(uid)
        print u.to_tsv()


if __name__ == "__main__":
    main()
