"""
VKontake HTTP API implementation stub
http://vk.com/pages?oid=-1&p=%D0%9E%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B5_%D0%BC%D0%B5%D1%82%D0%BE%D0%B4%D0%BE%D0%B2_API
"""

__author__ = 'Nikolay Anokhin, Vladimir Kulpinov'

import datetime
import time
import csv

import user
from api import Api


class VkApi(Api):
    endpoint = "https://api.vk.com/method/{method}"

    def get_friend_ids(self, uid):
        json = self.call("friends.get", uid=uid)
        for friend_id in json.get("response", []):
            yield str(friend_id)

    def get_profiles(self, uid_list):
        uids = ",".join(uid_list)
        json = self.call("getProfiles", uids=uids,
                         fields="sex,status,contacts,universities,relation,city,verified,bdate,personal")
        if json is not None:
            for user_json in json.get("response", []):
                yield self.json_to_user(user_json)

    def get_users(self, uid_list):
        num_attempts = 10
        uids = ",".join(uid_list)

        for i in range(0, num_attempts):
            json = self.call("users.get", uids=uids, fields="uid,first_name,last_name,sex,bdate,universities,counters")
            response_cur = json.get("response", [])
            if (len(response_cur) == 0):
                time.sleep(1)
                continue
            else:
                for user_json in response_cur:
                    yield self.json_to_user(user_json)
                break

    @staticmethod
    def json_to_user(json):
        u = user.User(json['uid'], json['first_name'], json['last_name'])
        university = json.get('universities')

        counters = json.get('counters')
        if counters:
            u.count_audios = counters['audios']
            u.count_friends = counters['friends']
            #u.count_groups = counters['groups']
            u.count_pages = counters['pages']
            u.count_photos = counters.get('photos', 0) + counters.get('user_photos', 0)

        if university and len(university) != 0:
            u.is_university = True
            u.grad_university = university[0].get('graduation')

        u.sex = json.get('sex', 0)

        if json.get('relation'):
            u.relation = json.get('relation')

        if json.get('status') and len(json.get('status')) > 0:
            u.is_exist_status = True
        try:
            bdate = json.get('bdate')
            u.set_age(VkApi.parse_birth_date(bdate))
        except ValueError:
            print u
            exit(1)
        return u

    @staticmethod
    def parse_birth_date(birth_date_str):
        if birth_date_str:
            parts = birth_date_str.split('.')
            if len(parts) == 3:
                try:
                    return datetime.date(int(parts[2]), int(parts[1]), int(parts[0]))
                except ValueError:
                    print "Wrong birthday " + birth_date_str
                    raise
            else:
                return datetime.date(1994, 9, 1)
        else:
            return datetime.date(1994, 9, 1)


def main():
    obfuscation = True

    token = "84e36c4b1d2a099efcb1e385d16f1a30ef13ca8f9bc13ea1166d5c3dc03c3cd1d502ff3be1e6be0393c96"
    user_id = "23959400"
    api = VkApi(token)

    csvfile = open('vk_base.csv', 'wb')
    vk_base_writer = csv.writer(csvfile)
    vk_base_writer.writerow(['UID', 'Name', 'Surname', 'Sex', 'Age', 'Audios', 'Photos', 'InterestPages', 'Friends'])

    counter_users = 0
    uids_to_check = [str(item) for item in api.get_friend_ids(user_id)]
    for pos in uids_to_check:
        for u in api.get_users([pos]):
            if (u.is_relevant()):
                print str(counter_users + 1) + " " + u.to_tsv(obfuscation)
                counter_users += 1
                vk_base_writer.writerow(u.to_tsv(obfuscation).encode('utf-8').split('\t'))
            else:
                pass

    csvfile.close()


if __name__ == "__main__":
    main()