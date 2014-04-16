from api import Api
import json
import scripts
import time
import sys

class User(Api):
  endpoint = 'https://api.vk.com/method/{method}'
  
  def __init__(self, access_token, count = 0):
    Api.__init__(self, access_token)
    self.count = count

  def get_friends(self, uid):
    data = self.call('friends.get', uid = uid,
                fields = "sex", count = self.count)
    return self.out(data, 0, lambda x: { key: x[key] for key in \
            ['uid', 'sex'] })

  def get_info(self, uids):
    data = self.call('users.get', uids = uids, fields = "sex")
    l = self.out(data, 0, lambda x: x)
    if len(l) == 1:
      return l[0]
    else:
      print >> sys.stderr, data
      return []

  def get_groups(self, uid):
    data = self.call('groups.get', uid = uid, count = self.count)
    return self.out(data, 1)

  def get_subscriptions(self, uid):
    data = self.call('users.getSubscriptions', uid = uid, extended = 1)
    if 'response' in data:
      data = filter(lambda x: x['type'] == 'page', data['response'])
      return map(lambda x: { key: x[key] for key in \
                  ['gid', 'name', 'type', 'is_closed', 'screen_name'] }, data)
    return []
  
  def wall_count(self, uid):
    data = self.call('wall.get', owner_id = uid, count = 1)
    if 'response' in data:
      return data['response'][0]
    return 0
  
  def albums_count(self, uid):
    data = self.call('photos.getAlbumsCount', uid = uid, count = 1)
    if 'response' in data:
      return data['response']
    return 0

  def get_wall(self, uid):
    data = self.call('wall.get', owner_id = uid, count = self.count)
    return self.out(data, 1, lambda x: { key:x[key] for key in \
                ['text', 'likes', 'comments', 'reposts', 'date', 'id'] })

  def get_audio(self, uid):
    data = self.call('audio.get', uid = uid, count = self.count)
    return self.out(data, 0, lambda x: x[u'artist'])

  def get_album_ids(self, uid):
    data = self.call('photos.getAlbums', uid = uid, count = self.count)
    return self.out(data, 0, lambda x: x['aid'])

  def get_photos_in_album(self, uid, aid):
    data = self.call('photos.get', uid = uid, aid = aid,
                                  extended = 1)
    return self.out(data, 0, lambda x: { key:x[key] for key in \
                    ['pid', 'text', 'likes', 'comments', 'created'] })

  def get_albums(self, uid):
    aids = self.get_album_ids(uid)
    l = []
    for album in aids:
      photos = self.get_photos_in_album(uid, album)
      l.append(scripts.create_album(album, photos))
    return l

  def get_data(self, uid, timeout = 1):
    person = scripts.create_person()
    person['info'] = self.get_info(uid)
    person['subscripts'] = self.get_subscriptions(uid)
    time.sleep(timeout)
    person['audio'] = self.get_audio(uid)
    person['wall'] = self.get_wall(uid)
    time.sleep(timeout)
    person['friends'] = self.get_friends(uid)
    person['albums'] = self.get_albums(uid)
    return person

  def check_data(self, data):
    empty = []
    for k in data.keys():
      if data[k] == [] or data[k] == '' or data[k] == 0 or data[k] == '0':
        empty.append(k)
    if len(empty) > 0:
      print 'Empty fields: {}'.format(empty)

  def walk(self, uid, timeout = 1, verbose = True):
    data = scripts.create_dict()
    root = self.get_data(uid)
    total = len(root['friends'])
    bad = 0
    for i, friend in enumerate(root['friends']):
      if verbose == True:
        print 'Processing: {} / {}'.format(i + 1, total)
      leaf = self.get_data(friend['uid'])
      self.check_data(leaf)
      if not 'sex' in leaf['info']:
        print >> sys.stderr, 'Error: empty answer'
        continue
      sex = leaf['info']['sex']
      if sex == 1 or sex == '1' or sex == 2 or sex == '2':
        data[str(sex)].append(leaf)
      else:
        bad += 1
        if verbose == True:
          print 'Bad friend'
      time.sleep(timeout)
    if verbose == True:
      print 'Total bad friends: {}'.format(bad)
    return data


  def out(self, data, start = 0, func = lambda x: str(x)):
    if 'response' in data:
      return map(func, data['response'][start:])
    return []
