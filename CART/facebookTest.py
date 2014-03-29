import requests #pip install requests
import json 
import facebook #pip install facebook-sdk

ACCESS_TOKEN = 'CAACEdEose0cBAPa3BamP4mge3ImK10ZBZAExEJDRGJicWDZAzu1K722ZBjpfbM1CRIkxJrkwrtgMgMEkmm3xghJWI3mPexjvRwOay46SBOpLCBmPZBP6wsRGf6D6ocIXZC7t6cAMQNZAXSEQDmArnSZCOYIHMemeXCv1jyRckQYuquGHMZCsdmZAz9ayZBkZA8QrNMcZD' 
base_url = 'https://graph.facebook.com/me'

def pp(o): 
    print json.dumps(o, indent=1)

g = facebook.GraphAPI(ACCESS_TOKEN)

friends = g.get_connections('me', 'friends')
all = 0
withRelations = 0
for connection in friends['data']:    
    friend = g.get_object(connection['id'])
    if (friend.has_key('birthday')):
        if len(friend['birthday']) == 10:
            age = 2014 - int(friend['birthday'][6:10])
            if age < 100:
                
                all += 1
                if friend.has_key('relationship_status'):
                    withRelations += 1
                    print age, friend['relationship_status'], friend['first_name'], friend['last_name']
print all
print withRelations  
