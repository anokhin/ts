"""
VKontake HTTP API implementation stub
http://vk.com/pages?oid=-1&p=%D0%9E%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B5_%D0%BC%D0%B5%D1%82%D0%BE%D0%B4%D0%BE%D0%B2_API
"""

__author__ = 'Nikolay Anokhin'

import datetime
import user
from api import Api
import numpy as np
import time
import lang


class VkApi(Api):

    endpoint = "https://api.vk.com/method/{method}"

    def get_friend_ids(self, uid):
        json = self.call("friends.get", uid=uid)
        for friend_id in json.get("response", []):
            yield str(friend_id)

    def get_users(self, uid_list):
        uids = ",".join(uid_list)
        json = self.call("users.get", uids=uids, fields="uid,first_name,last_name,sex,bdate")
        #print json
        for user_json in json.get("response", []):
            yield self.json_to_user(user_json)

    def get_groups(self, uid):
        groups = self.call("groups.get", uid = uid, extended = 1)

        gr_array = groups.get("response", [])[1:]        

        for group in gr_array:
            yield  self.group_name(group)

    '''def get_full_groups_list(self, uid_list):
        groups_list = []

        uids = ",".join(uid_list)
        json = self.call("users.get", uids=uids, fields="uid")

        users = json.get("response", [])
        n_users = len(users)

        for user_json in users:
            groups = get_groups(user_json['uid'])
            buff = zeros(n_users)            
            for g in groups:'''

        #def tokenizer(self, str): #to be defined


    def get_all_tokens_alpha(self, uid_list):

        uids = ",".join(uid_list)

        #uids = uid_list

        json = self.call("users.get", uids=uids, fields="uid,sex,first_name, last_name")

        users = json.get("response", [])
        n_users = len(users)

        print n_users

        token_user_table = np.zeros((n_users,1))
        vocab = []
        test_vocab = []
        test_sex = 0

        for i in range(0,n_users-1):
            token_user_table[i,0] = users[i]["sex"]

            #print (users[i]["first_name"],users[i]["last_name"])
            print users[i]["uid"]
            print ('vocab size: ',len(vocab))

            counter = 0
            isfirst = 1

            for g in self.get_groups(users[i]["uid"]):

                if not( g in vocab ):
                    vocab.append(g)
                    token_user_table = np.append(token_user_table, np.zeros((n_users, 1)),1)
                    

                    counter += 1

                token_user_table[i, vocab.index(g) + 1] += 1

                if isfirst ==1:
                    test_vocab.append(g)

            if isfirst == 1:
                isfirst =0
                test_sex = users[i]["sex"]


            print ('new tokens:', counter)
            #print token_user_table
            #raw_input("continue")
            #time.sleep(7)


        

        token_gen_table = np.zeros((len(vocab),2))

        for i in range(1,len(vocab)):
            buff_m = 0
            buff_f = 0
            for j in range(0,n_users):
                if token_user_table[j,i] <> 0:
                    token_gen_table[i-1, token_user_table[j,0] - 1] += token_user_table[j,i]


        return (vocab, token_gen_table, token_user_table, test_vocab, test_sex) 









    @staticmethod
    def json_to_user(json):
        u = user.User(json['uid'], json['first_name'], json['last_name'])
        u.sex = json.get('sex')
        u.set_age(VkApi.parse_birth_date(json.get('bdate')))
        return u

    @staticmethod
    def group_name(group):
        result = group['name']
        return result    

    @staticmethod
    def parse_birth_date(birth_date_str):
        if birth_date_str:
            parts = birth_date_str.split('.')
            if len(parts) == 3:
                return datetime.date(int(parts[2]), int(parts[1]), int(parts[0]))


def main():
    token = "a90280565372776a5415a352befdcbeb013794af62ecbc0f7c295d322364bfc8ac2a08fc82e39fa031560"
    api = VkApi(token)

    my_uid = 3816268

    uids = api.get_friend_ids("3816268")

    vocab, token_gen_table, token_user_table, test_vocab, test_sex= api.get_all_tokens_alpha(uids)


    Mult = Data(vocab, token_gen_table, token_user_table)

    status = -1

    while (status <> 0):
        status = raw_input("0 - exit, 1 - train, 2 - apply")

        if status == 1:
            Mult.train("MultinomialLaplase")
            print "Training complete\n\n"
        elif status == 2:
            pred_sex = Mult.apply(test_vocab)

            if pred_sex == test_sex:
                print "prediction is correct"
            else:
                print "prediction is incorrect"

    #api.get_all_tokens_alpha(uids)
    '''for u in api.get_users(uids):
        print u.to_tsv()'''

   # for g in api.get_groups(my_uid):
       # print g

if __name__ == "__main__":
    main()