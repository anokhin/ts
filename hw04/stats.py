from api import Api
import json
import sys

class Stats(Api):
  endpoint = 'https://api.vk.com/method/{method}'

  def friend_ids(self, uid):
    data = self.call('friends.get', uid=uid)
    return map(lambda x: str(x), data['response'])

  def friends_count(self, uid):
    data = self.call('friends.get', uid=uid)
    if 'response' in data:
      return str(len(data['response']))
    return 'error'

  def groups_count(self, uid):
    data = self.call('groups.get', uid=uid, count='1')
    return self.out(data, 0)

  def wall_post_count(self, uid):
    data = self.call('wall.get', owner_id=uid, count='1')
    return self.out(data, 0)

  def audio_count(self, uid):
    data = self.call('audio.getCount', owner_id=uid)
    return self.out(data)

  def album_count(self, uid):
    data = self.call('photos.getAlbumsCount', uid=uid)
    return self.out(data)

  def get_user_stats(self, uid):
    return {"friends_count": self.friends_count(uid),
            "groups_count": self.groups_count(uid),
            "wall_post_count": self.wall_post_count(uid),
            "audio_count": self.audio_count(uid),
            "album_count": self.album_count(uid)}

  def users_sex(self, uids):
    data = self.call('users.get', uids=uids, fields='sex')
    return [ str(person['sex']) for person in data['response'] ]

  def out(self, data, index=""):
    if 'response' in data:
      if index == "":
        return str(data['response'])
      return str(data['response'][0])
    return 'error'


def mean(l):
  if len(l) == 0:
    return 0
  return sum(l) / len(l);


def main():
  params_file = open('params.conf', 'r')
  params = json.load(params_file)
  params_file.close()
  api = Stats(params['token'])
  my_uid = params['my_uid']
  ids = api.friend_ids(my_uid)
  sexes = api.users_sex(','.join(ids))
  data = []
  statistics = {'groups_count' : [[],[]],
                'audio_count' : [[],[]],
                'wall_post_count' : [[],[]],
                'friends_count' : [[],[]],
                'album_count' : [[],[]]}
  for i, person_id in enumerate(ids):
    data.append((sexes[i], api.get_user_stats(person_id)))
    (sex, val) = data[-1]
    if sex == '1' or sex == '2':
      for k, v in val.items():
        if v != 'error':
          statistics[k][int(sex) - 1].append(int(v))
    print >> sys.stderr, data[-1]
  print 'Women vs men:'
  for k, v in statistics.items():
    print k + ':', mean(v[0]), 'vs',  mean(v[1])
    

if __name__ == '__main__':
  main()
