import tweepy
import pandas as pd
import time
import re
import os

path = os.getcwd()
CONSUMER_KEY = '7NId71jMVK1ZLQ5pPp3wIK6YL'
CONSUMER_SECRET = '7FsNm7Q7hz0LuAbs1AsIpaWlibVxur9suInSKbuu9Ilbu88DDr'
ACCESS_KEY = '1244214884683755521-fnMyyltyVhp5Sp0EH0waIRUKodj3rT'
ACCESS_SECRET = 'uXAuA098t9zxPCYwaodmfrymvBqXZFcLFSAwUb5pmjNOw'
covid_hospitals = pd.read_csv("ICMRTestingLabs.csv")
hospitals = pd.read_csv("devfest.csv")


auth=tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api=tweepy.API(auth)

def bot():
    f=open("names.txt","r")
    name = f.readline()
    while name:
        api.update_status("Hello {}! Nice to meet you.".format(name.strip()))
        name=f.readline()
        time.sleep(30)
    f.close()

file = 'last_seen_id.txt'

def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id

def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return
mentions = api.mentions_timeline()
print(mentions[0].text, mentions[0].id)
store_last_seen_id(mentions[0].id, file)


def find_hospitals(pincode):
            pincode[0].strip()
            hospital_area = pd.DataFrame()
            hospital_area = hospitals[hospitals["Pincode"] == pincode[0]]
            hosp = hospital_area.reset_index()
            hosp = hosp.drop(['index'], axis = 1)
            hosp
            total_rows=len(hosp.axes[0])
            hosp.columns
            name = hosp['Hospital_Name']
            hosp.drop(labels=['Hospital_Name'], axis=1,inplace = True)
            hosp.insert(0, 'Hospital_Name', name)
            print(total_rows)
            hosp
            dict = {}
            hosp_list = []
            string = ""
            dict = hosp.to_dict()
            print(dict.keys())
            for i in range(total_rows):
                dict['Hospital_Name'][i] = dict['Hospital_Name'][i] + ', '
                dict['State'][i] = dict['State'][i] + ', '
                dict['District'][i] = dict['District'][i] + ', '
                dict['Location'][i] = dict['Location'][i] + ' '

            hosp_list = []
            for i in range(total_rows):
                string = ''
                for j in dict.keys():
                    string = string + dict[j][i]
                hosp_list.append(string)
            return(hosp_list, total_rows)


cities = []
cities = covid_hospitals.city.unique()
states = covid_hospitals.state.unique()
def covid_hospitals_list(state):
    covid_list = pd.DataFrame()
    covid_list = covid_hospitals[covid_hospitals['state'] == state]
    total1 = len(covid_list.axes[0])
    covid_list
    covid_list = covid_list.reset_index()
    covid_list = covid_list.drop(['index'], axis = 1)
    covid_list.columns
    pincode = covid_list['pincode']
    lab = covid_list['lab']
    hosp_type = covid_list['type']
    state = covid_list['state']
    city = covid_list['city']
    covid_list.drop(['pincode','type', 'lab','state','city'], axis = 1, inplace = True)
    #covid_list['pincode'] = pincode
    #covid_list['type'] = hosp_type
    covid_list
    dict = {}
    dict = covid_list.to_dict()
    hosp_list = []
    for i in range(total1):
        string = ''
        for j in dict.keys():
            string = string + str(dict[j][i])
        hosp_list.append(string)
    return(hosp_list, total1)


def reply_to_tweets():
    print('retrieving and replying to tweets...', flush=True)
    last_seen_id = retrieve_last_seen_id(file)
    # NOTE: We need to use tweet_mode='extended' below to show
    # all full tweets (with full_text). Without it, long tweets
    # would be cut off.
    mentions = api.mentions_timeline(last_seen_id, tweet_mode='extended')
    for mention in reversed(mentions):
        
        
        if 'corona' in mention.full_text.lower() or 'covid' in mention.full_text.lower():
            print("COVID tweet found!")
            total_covid = 0
            for i in states:
                if i in mention.full_text:
                    hosp_list, total_covid = covid_hospitals_list(i)
                    break
            if total_covid == 0:
                 api.update_status('@' + mention.user.screen_name + ' ' + 'Uh oh! Unforturnately, we could not find any hospitals in this pin code. Kindly enter another pincode.' , mention.id)
            else:
                for i in range(total_covid):
                    api.update_status('@' + mention.user.screen_name + ' ' + hosp_list[i] , mention.id)
                    time.sleep(1)
            
        else:
            pin_code = re.findall(r' (\d{6})', mention.full_text)
            print("Found Tweet!")
            if len(pin_code) != 0:
                hosp_list, total = find_hospitals(pin_code)
                if total == 0:
                     api.update_status('@' + mention.user.screen_name + ' ' + 'Uh oh! Unforturnately, we could not find any hospitals in this pin code. Kindly enter another pincode.' , mention.id)
                else:
                    for i in range(total):
                        api.update_status('@' + mention.user.screen_name + ' ' + hosp_list[i] , mention.id)
                        time.sleep(1)
            
        print(str(mention.id) + ' - ' + mention.full_text, flush=True)
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, file)


while True:
    reply_to_tweets()
    time.sleep(1)
