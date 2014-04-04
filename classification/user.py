from datetime import date


class User(object):
    def __init__(self, uid=None, first_name=None, last_name=None):
        self.uid = uid
        self.first_name = first_name
        self.last_name = last_name
        self.sex = 0
        self.age = None
        self.grad_university = None
        self.relation = 0
        self.is_exist_status = False
        self.count_friends = 0
        self.count_photos = 0
        self.count_audios = 0
        self.count_groups = 0
        self.count_pages = 0

    def set_age(self, birth_date):
        if birth_date:
            self.age = int((date.today() - birth_date).days / 365.2425)

    def is_relevant(self):
        return self.sex and self.sex > 0 and self.count_friends > 0 and self.count_friends < 500

    def to_tsv(self, obfuscate=False):
        if not obfuscate:
            return '\t'.join([unicode(self.uid), unicode(self.first_name), unicode(self.last_name),
                           unicode(self.sex), unicode(self.age), unicode(self.count_audios),
                           unicode(self.count_photos), unicode(self.count_pages),
                           unicode(self.count_friends)])
        else:
            return '\t'.join([unicode(1), unicode('Vasya'), unicode('Vasya'),
                           unicode(self.sex), unicode(self.age), unicode(self.count_audios),
                           unicode(self.count_photos), unicode(self.count_pages),
                           unicode(self.count_friends)])


    def from_tsv(self, row):
        try:
            self.uid = row[0]
            self.first_name = row[1].decode('utf-8')
            self.last_name = row[2].decode('utf-8')
            self.sex = row[3]
            self.age = row[4]
            self.count_audios = row[5]
            self.count_photos = row[6]
            self.count_pages = row[7]
            #self.count_groups = row[8]
            self.count_friends = row[8]
        except:
            print "Error while reading user from row"
            raise BaseException

    def get_predictable(self):
        result = []
        result.append(int(self.sex))
        result.append(int(self.count_photos))
        result.append(int(self.count_pages))
        result.append(int(self.count_audios))
        return result

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return u"User('{uid}', '{first}', '{last}')".format(uid=self.uid, first=self.first_name, last=self.last_name)
