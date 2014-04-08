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
from datetime import date


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
                try:
                    return datetime.date(
                        int(parts[2]), int(parts[1]), int(parts[0]))
                except ValueError:
                    return None


def get_uid(json_dict):
    return json_dict.get(u'uid', u'0')
get_uid.required_fields = frozenset([u'uid'])


def get_first_name(json_dict):
    return json_dict.get(u'first_name', u'')
get_first_name.required_fields = frozenset([u'first_name'])


def get_last_name(json_dict):
    return json_dict.get(u'last_name', u'')
get_last_name.required_fields = frozenset([u'last_name'])


def get_sex(json_dict):
    return json_dict.get(u'sex', u'0')
get_sex.required_fields = frozenset([u'sex'])


def get_age(json_dict):
    parsed_birthday = VkApi.parse_birth_date(json_dict.get(u'bdate'))
    if parsed_birthday is None:
        return None
    return int((date.today() - parsed_birthday).days / 365.2425)
get_age.required_fields = frozenset([u'bdate'])


def get_has_mobile(json_dict):
    return json_dict.get(u'has_mobile', u'0')
get_has_mobile.required_fields = frozenset([u'has_mobile'])


def get_graduation(json_dict):
    """
    Returns relative years between current year and graduation year
    Return value of 5 means the graduation happened 5 years ago.
    Return value of -5 means the graduation will happen in 5 years.
    """
    graduation = json_dict.get(u'graduation', None)
    if graduation == 0 or graduation is None:
        return None
    return date.today().year - graduation
get_graduation.required_fields = frozenset([u'education'])


def get_school_start(json_dict):
    """
    Returns amount of how many years ago the user started
    his first school (first mentioned on vk).
    If he has no mentioned school start years, return None
    """
    try:
        schools = json_dict[u'schools']
    except KeyError:
        return None
    MAGICAL_MAX_START_YEAR = 9999
    start_years = [
        school.get(u'year_from', MAGICAL_MAX_START_YEAR) for school in schools]
    if len(start_years) == 0:
        return None
    min_year = min(start_years)
    if min_year == MAGICAL_MAX_START_YEAR:
        return None
    current_year = date.today().year
    return current_year - min_year
get_school_start.required_fields = frozenset([u'schools'])


def get_school_end(json_dict):
    """
    Returns how many years ago the user finished his latest school
    (the school with maximum year_to on vk)
    If he has no mentioned schools with year_to, return None
    """
    try:
        schools = json_dict[u'schools']
    except KeyError:
        return None
    MAGICAL_MAX_END_YEAR = -9999
    end_years = [
        school.get(u'year_to', MAGICAL_MAX_END_YEAR) for school in schools]
    if len(end_years) == 0:
        return None
    max_year = max(end_years)
    if max_year == MAGICAL_MAX_END_YEAR:
        return None
    current_year = date.today().year
    return current_year - max_year
get_school_end.required_fields = frozenset([u'schools'])


def get_required_fields(target_fields):
    required_fields = set()
    for k, v in target_fields.iteritems():
        required_fields.update(v.required_fields)
    return required_fields


def median(lst):
    return sorted(lst)[len(lst)//2]


def get_median_age_of_friends(json_dict):
    """
    Returns median of ages of all friends of the user
    """
    all_uids = [x for x in api.get_friend_ids(json_dict[u'uid'])]
    uids_in_parts = [all_uids[i:i+100] for i in range(0, len(all_uids), 100)]
    target_fields = {
        u'uid': get_uid,
        u'age': get_age,
    }
    required_fields = get_required_fields(target_fields)
    ages = []
    for uids in uids_in_parts:
        response_dicts = api.get_jsons(uids, required_fields)
        processed_users = [process_user(target_fields, user)
                           for user in response_dicts]
        ages.extend([user[u'age']
                     for user in processed_users if user[u'age'] is not None])

    return unicode(str(median(ages)))
get_median_age_of_friends.required_fields = frozenset([u'age'])


def user_dict_to_line(user, fields, delimeter=u'\t'):
    result = u""
    for field in fields:
        result += unicode(user[field])
        result += delimeter
    return result[:-1]


def process_user(target_fields, user_dict):
    """
    Takes a dict with items like this
    u'target_field': function_name
    and a user dict
    The function must have 'required_fields' value and take user dict as arg
    returns a dict with target fields
    """
    new_dict = {}
    for k, v in target_fields.iteritems():
        new_dict[k] = v(user_dict)
    return new_dict

api = None


def main():
    token = argv[1]
    user_uid = argv[2]

    global api
    api = VkApi(token)
    uids = api.get_friend_ids(user_uid)
    target_fields = {
        u'uid': get_uid,
        u'first_name': get_first_name,
        u'last_name': get_last_name,
        u'sex': get_sex,
        u'age': get_age,
        u'graduation': get_graduation,
        u'school_start': get_school_start,
        u'school_end': get_school_end,
        u'friends_age': get_median_age_of_friends,
    }
    target_fields_list = [k for k in target_fields.iterkeys()]
    required_fields = get_required_fields(target_fields)

    response_dicts = api.get_jsons(uids, required_fields)
    without_deactivated = [x for x in response_dicts
                           if u'deactivated' not in x]
    processed_users = [
        process_user(target_fields, user) for user in without_deactivated
    ]

    if len(argv) >= 5 and argv[4] == "--append":
        output_file = io.open(argv[3], "a", encoding='utf-8')
    else:
        if (len(argv) == 4):
            output_file = io.open(argv[3], "w", encoding='utf-8')
        else:
            output_file = sys.stdout
        output_file.write(u'\t'.join(target_fields_list) + u'\n')

    output_file.write(u'\n'.join(
        [user_dict_to_line(user, target_fields_list)
         for user in processed_users]
    ))


if __name__ == "__main__":
    main()
