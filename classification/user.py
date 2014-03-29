from datetime import date
import json

class User(object):

    def __init__(self, uid, first_name, last_name):
        self.set_defaults()
        self.uid = uid
        self.first_name = first_name
        self.last_name = last_name

    def __init__(self, **kwargs):
        self.set_defaults()
        self.set_args(**kwargs)

    def set_defaults(self):
        self.uid = None
        self.first_name = None
        self.last_name = None
        self.sex = None
        self.age = None
        self.relationship = None
        self.first_work = None
        self.last_education = None

    def set_args(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def get_data_for_regression(self):
        return dict(
            age=self.age,
            #correlation between age and (sex x relationship)
            sex=self.sex,
            relationship=self.relationship,
            #correlation between age and graduate or/and becoming employee year
            first_work=self.first_work,
            last_education=self.last_education,
            #most important feature
            one=1
        )

    @staticmethod
    def date_to_years(date):
        return int((date.today() - date).days / 365.2425)

    def set_age(self, birth_date):
        if birth_date:
            self.age = self.date_to_years(birth_date)

    def to_tsv(self):
        return u'\t'.join([unicode(self.uid), unicode(self.first_name), unicode(self.last_name), unicode(self.sex), unicode(self.age)])

    def __str__(self):
        #return unicode(self).encode('utf-8')
        return str(self.__dict__)

    def __unicode__(self):
        return u"User('{uid}', '{first}', '{last}')".format(uid=self.uid, first=self.first_name, last=self.last_name)
