import os
import requests

def checkBlacklist(userId):
    with open("blacklist.txt") as blacklist:
        if str(userId) in blacklist.read():
            return True
        else:
            return False

def checkVote(userId):
    check = requests.get("https://top.gg/api/bots/913442195388903467/check?userId={}".format(str(userId)), headers={"Authorization": os.environ['TOPGG_AUTH']})
    if check.json().get("voted") == 1:
        return True
    else:
        return False

def replaceAll(str, char, rechar):
    newstr = str.replace(char, rechar)
    if newstr == str: return False
    else: return newstr