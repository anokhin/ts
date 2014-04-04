"""
to get token visit:
oauth.vk.com/authorize?client_id=1&scope=friends,photos,video,audio,groups,wall&redirect_uri=https://oauth.vk.com/blank.html&display=page&v=5.12&response_type=token

VKontake HTTP API implementation stub
http://vk.com/pages?oid=-1&p=%D0%9E%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B5_%D0%BC%D0%B5%D1%82%D0%BE%D0%B4%D0%BE%D0%B2_API
"""

import datetime
import user
from api import Api
import csv
import time

class VkApi(Api):

    endpoint = "https://api.vk.com/method/{method}"

    def get_friend_ids(self, uid):
        json = self.call("friends.get", uid=uid)
        for friend_id in json.get("response", []):
            yield str(friend_id)


    def get_users(self, uid_list):
      uid_list = [uid for uid in uid_list]
      i = 0
      while i<=len(uid_list):
        uids = ",".join(uid_list[i:i+100])
        i += 100
        json = self.call("users.get", uids=uids, fields="uid,first_name,last_name,sex,interests, movies, tv, books, games, about")
        for user_json in json.get("response", []):
            u = self.json_to_user(user_json)
            time.sleep(0.2)
            u.about += ","+",".join([ group['name'] for group in self.call("groups.get", uid=u.uid, extended=1).get("response", [])[1:]])
#            time.sleep(0.2)
#            u.wall = [note['text']   for note  in wall_notes]
#            for id in [note['id'] for note in wall_notes]:
#                time.sleep(0.2)
#                for c in self.call("wall.getComments", post_id=id, owner_id=u.uid).get("response",[])[1:]:
#                    u.wall.append(c['text'])

#            u.albums =     [ album['title'] for album in self.call("photos.getAlbums", uid=u.uid, fields="title").get("response", [])]
#            audios = self.call("audio.get", uid=u.uid).get("response", [])
#            u.audios  =     [ audio['title']  for audio in audios]
#            u.artists =     [ audio['artist'] for audio in audios]
            yield u
#
    @staticmethod
    def json_to_user(json):
        u = user.User(json['uid'], json['first_name'], json['last_name'])
        u.sex = json.get('sex')
        u.about = ",".join([json.get(x,'') for x in ['interests', 'movies', 'tv', 'books', 'games', 'about']])
        return u


def main():
    token =  ""
    api = VkApi(token)
    uids = api.get_friend_ids("")

    f = open('data.csv', 'w')
    cfw = csv.writer(f, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)

    for u in api.get_users(uids):
        cfw.writerow(u.to_csv())

    f.close()



if __name__ == "__main__":
    main()
