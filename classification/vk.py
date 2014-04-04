"""
VKontake HTTP API implementation stub
http://vk.com/pages?oid=-1&p=%D0%9E%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B5_%D0%BC%D0%B5%D1%82%D0%BE%D0%B4%D0%BE%D0%B2_API
"""

__author__ = 'Nikolay Anokhin'

import datetime
import user
import io
import sys
from sys import argv
from api import Api


class VkApi(Api):

    endpoint = "https://api.vk.com/method/{method}"

    def get_friend_ids(self, uid):
        json = self.call("friends.get", uid=uid)
        for friend_id in json.get("response", []):
            yield str(friend_id)

    def get_jsons(self, uid_list, fields):
        uids = ",".join(uid_list)
        json = self.call(
            "users.get",
            uids=uids,
            fields=",".join(fields))
        for user_json in json.get("response", []):
            yield user_json

    def get_json(self, uid, fields):
        return self.call(
            "users.get",
            uids=uid,
            fields=",".join(fields)
        )

    @staticmethod
    def json_to_user(json):
        u = user.User(json['uid'], json['first_name'], json['last_name'])
        u.sex = json.get('sex')
        u.set_age(VkApi.parse_birth_date(json.get('bdate')))
        return u

    """use this when vk starts returning request for captcha
    instead of actual responses"""
    def send_captcha_answer(self):
        return self.call("users.get",
                         captcha_sid='',
                         captcha_key=''
                         )

    @staticmethod
    def parse_birth_date(birth_date_str):
        if birth_date_str:
            parts = birth_date_str.split('.')
            if len(parts) == 3:
                return datetime.date(
                    int(parts[2]), int(parts[1]), int(parts[0]))


def main():
    token = argv[1]
    user_uid = argv[2]
    if (len(argv) >= 4):
        output_file = io.open(argv[3], "w", encoding='utf-8')
    else:
        output_file = sys.stdout
    api = VkApi(token)
    uids = api.get_friend_ids(user_uid)
    fields = ["uid", "first_name", "last_name", "sex", "bdate",
              "has_mobile", "education"]
    jsons = [api.get_json(uid, fields) for uid in uids]

    output_file.write(u"uid\tfirst_name\tlast_name\tsex\tage\n")
#    for u in api.get_users(uids):
#        print u.to_tsv().encode('utf-8')


if __name__ == "__main__":
    main()
