#!/usr/bin/env python3
# pip install searchtweets


from searchtweets import load_credentials
import requests
import yaml
import json
import datetime

def getdatetimestamp():
    currenttime = datetime.datetime.now().strftime("%Y%m%d%H%m%S%f")
    return currenttime


def create_twitter_url(handle,next_token):
    max_results = 100
    mrf = "max_results={}".format(max_results)
    fields = "tweet.fields=author_id,created_at,lang,source"
    # https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/tweet
    q = "query=from:{}".format(handle)
    if next_token == "":
        nt = ""
    else:
        nt = "next_token={}".format(next_token)

    url = "https://api.twitter.com/2/tweets/search/recent?{}&{}&{}&{}".format(
        mrf, q, fields, nt
    )

    return url


def process_yaml():
    with open(".twitter_keys.yaml") as file:
        return yaml.safe_load(file)


def create_bearer_token(data):
    return data["search_tweets_api"]["bearer_token"]


def twitter_auth_and_connect(bearer_token, url):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    response = requests.request("GET", url, headers=headers)
    return response.json()


def main():
    #handles = ["GrantMoyleROI"]
    handles = ["GrantMoyleROI","ROITraining","MSNBC","NASA","TWITTER"]
    for handle in handles:
        i = 0
        tweetfile = handle + getdatetimestamp() + ".json"
        outfile = open("TwitterOut/" + tweetfile,"w")
        next_token=""
        while  i < 100: # Read a maximum of 100 pages of tweets (each containing up to 100 tweets)
            rawfilename = "raw" + handle + getdatetimestamp() + ".json"
            url = create_twitter_url(handle,next_token)
            data = process_yaml()
            bearer_token = create_bearer_token(data)
            res_json = twitter_auth_and_connect(bearer_token, url)
            print(type(res_json))

            # Write Raw Tweets to File
            rawoutfile = open("Raw/" + rawfilename,"w")
            json.dump(res_json,rawoutfile)
            rawoutfile.close()
        
            tweets=res_json["data"]
            for tweet in tweets:
                tweet['handle'] = handle
                print(handle)
                print(type(handle))
                print(json.dumps(tweet))
                json.dump(tweet,outfile)
                outfile.write('\n')
               
            meta=res_json["meta"]
            # print("newest_id: " + meta["newest_id"])
            if "next_token" in meta:
                next_token = meta["next_token"]
                print(next_token)
                #input("Press Enter to continue...")
                i += 1
            else:
                break
        outfile.close()

if __name__ == "__main__":
    main()