class User(object):

    def __init__(self, uid, first_name, last_name):
        self.uid = uid
        self.first_name = first_name
        self.last_name = last_name
        self.sex = None
        self.age = None
        self.albums = []
        self.wall = []
        self.audios = []
        self.artists = []
        self.about = []

    def to_csv(self):
        return [
                     self.to_str(self.uid)
                    ,self.to_str(self.first_name)
                    ,self.to_str(self.last_name)
                    ,self.to_str(self.sex)
                    ,self.to_str(self.about)
#                    ,",".join(map(self.to_str, self.albums))
#                    ,",".join(map(self.to_str, self.wall))
#                     ,",".join(map(self.to_str, self.artists))
#                    +",".join(map(self.to_str, self.audios))
        ]

    @staticmethod
    def to_str(x):
        return unicode(x).encode('utf-8')

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return u"User('{uid}', '{first}', '{last}')".format(uid=self.uid, first=self.first_name, last=self.last_name)
