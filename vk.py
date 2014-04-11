"""
VKontake HTTP API implementation stub
http://vk.com/pages?oid=-1&p=%D0%9E%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B5_%D0%BC%D0%B5%D1%82%D0%BE%D0%B4%D0%BE%D0%B2_API
"""

__author__ = 'Nikolay Anokhin'

import datetime
import numpy
import urllib2
import csv
import argparse

import user
from api import Api
def save_page(id):
    response = urllib2.urlopen('http://vk.com/id'+str(id))
    html = response.read()
    f = open(str(id)+'.html', 'wb')
    f.write(html)
    f.close()
def save_html(url, name):
    req = urllib2.Request(url)
    req.add_header("Referer", "http://vk.com/")
    html = urllib2.urlopen(req).read()
    f = open(name, 'wb')
    f.write(html)
    f.close()

def get_page_info(id):
    try:
        response = urllib2.urlopen('http://vk.com/id'+str(id))
        html = response.read()
    except:
        return -1, -1, -1
    w = html.find('<a name="wall">')
    if w!= -1:
        v = html[w:].find('slim_header')+w+len('slim_header>>')
        i = 0
        while not('0' <= html[v+i] and html[v+i] <= '9'):
            i = i+1
        v = v+i
        i = 0
        while '0' <= html[v+i] and html[v+i] <= '9':
            i = i+1
        try:
            wall = int(html[v:v+i])
        except:
            wall = -1
    else:
        wall = -1
    w = html.find('<a href="/albums')
    if w!= -1:
        v = html[w:].find('pm_counter')+w+len('pm_counter>>')
        i = 0
        while not('0' <= html[v+i] and html[v+i] <= '9'):
            i = i+1
        v = v+i
        i = 0
        while '0' <= html[v+i] and html[v+i] <= '9':
            i = i+1
        try:
            photo = int(html[v:v+i])
        except:
            photo = -1
    else:
        photo = -1
    w = html.find('act=idols')
    if w!= -1:
        v = html[w:].find('pm_counter')+w+len('pm_counter>>')
        i = 0
        while not('0' <= html[v+i] and html[v+i] <= '9'):
            i = i+1
        v = v+i
        i = 0
        while '0' <= html[v+i] and html[v+i] <= '9':
            i = i+1
        try:
            subs = int(html[v:v+i])
        except:
            subs = -1
    else:
        subs = -1

    return subs, wall, photo

class VkApi(Api):
    endpoint = "https://api.vk.com/method/{method}"

    def get_friend_ids(self, uid):
        json = self.call("friends.get", uid=uid)
        for friend_id in json.get("response", []):
            yield str(friend_id)
    def get_friend_recent(self, uid):
        json = self.call("friends.getRecent", uid=uid)
        res = []
        for friend_id in json.get("response", []):
            res.append(str(friend_id))
        return res

    def get_profiles(self, uid_list):
        uids = ",".join(uid_list)
        json = self.call("getProfiles", uids=uids,
                         fields="sex,status,contacts,relation")
        if json is not None:
            for user_json in json.get("response", []):
                yield self.json_to_user(user_json)

    def get_users(self, uid_list):
        uids = ",".join(uid_list)
        json = self.call("users.get", uids=uids, fields="uid,first_name,last_name,sex,bdate")
        for user_json in json.get("response", []):
            yield self.json_to_user(user_json)

    def json_to_user(self, json):
        u = user.User(json['uid'], json['first_name'], json['last_name'])
        ##university = json.get('universities')
        #if university and len(university) != 0:
        #    u.is_university = True
        #    u.grad_university = university[0].get('graduation')
        u.sex = json.get('sex')
        if json.get('relation'):
            u.relation = json.get('relation')
        if json.get('status') and len(json.get('status')) > 0:
            u.is_exist_status = 2
        else:
             u.is_exist_status = 1
        u.number_of_friends = len(self.call("friends.get", uid=u.uid).get("response", []))
        u.subscriptions, u.wall_len, u.photos = get_page_info(u.uid)
        #u.subscriptions = len(self.call("subscriptions.get", uid=u.uid).get("response", []))
        #u.wall_len = len(self.call("wall.get", uid=u.uid).get("response", []))
        #u.photos = len(self.call("photos.getProfile", uid=u.uid).get("response", []))
        return u

    @staticmethod
    def parse_birth_date(birth_date_str):
        if birth_date_str:
            parts = birth_date_str.split('.')
            if len(parts) == 3:
                try:
                    return datetime.date(int(parts[2]), int(parts[1]), int(parts[0]))
                except ValueError:
                    print(birth_date_str)
                    raise

def parse_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-t', dest='token', default="",
                   help='token of vk user')
    parser.add_argument('-r', dest='num_of_requests', default=20,
                   help='token of vk user', type =int)
    parser.add_argument('-o', dest='outfile', default='users.csv')
    return parser.parse_args()

def main():
    num_of_requests = 20
    num_of_ids = 10
    max_id = 240 * 1000 * 1000
    #https://oauth.vk.com/authorize?client_id=1&scope=friends&redirect_uri=https://oauth.vk.com/blank.html&display=page&v=5.12&response_type=token
    args = parse_args()
    token = args.token
    num_of_requests = args.num_of_requests
    api = VkApi(token)

    append = False
    outfile = parse_args().outfile
    try:
        with open(outfile, "r") as f:
            if f.readline():
                append = True
    except IOError:
        append = False
    with open(outfile, "ab") as f:
        field_names = ['id', 'firstname', 'lastname', 'gender', 'relationships', 'status', 'wall', 'subscriptions', 'photos', 'friends'];
        dw = csv.DictWriter(f, field_names)
        if not append:
            dw.writeheader()
        for r in range(0, num_of_requests):
            uids = []
            for i in range(0, num_of_ids):
                uid = numpy.random.randint(1, max_id)
                uids.append(str(uid))
            for u in api.get_profiles(uids):
                dw.writerow(dict(zip(field_names, u.to_list())))
            f.flush()
            print("req"+str(r))
    print("Ok")


if __name__ == "__main__":
    main()