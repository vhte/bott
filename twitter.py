import tweepy
import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup
from random import randint
from secrets import API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET


LIMIT_TWEET = 280
WIKIPEDIA = "https://en.wikipedia.org/wiki/"
THRESHOLD = "0000 - END"

def post_tweet(text):
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)

    result = api.update_status(text)
    return result.id

def decapitalize(expr):
    return r"On this day in {}, {}".format(expr.group(1), expr.group(2)[0].upper() + expr.group(2)[1:]) # TODO better lower()

now = datetime.now()
page_name = now.strftime("%B_{}".format(now.day)) # %d has a leading 0

wikipedia_page = requests.get(WIKIPEDIA + page_name)
if wikipedia_page.status_code != 200:
    raise Exception("Didn't get a good page on Wikipedia: [{}] {}".format(wikipedia_page.status_code, WIKIPEDIA + page_name))

parser = BeautifulSoup(wikipedia_page.content, "html.parser")

tmp_li = parser.new_tag("li")
tmp_li.string = THRESHOLD
parser.find(id="Births").insert_before(tmp_li)

events = parser.find_all("ul")
all_items = parser.find_all("li", class_=None)

triaged_items = []
for item in all_items:
    item_text = item.get_text()

    # Removing references on the page, e.g. [3]
    item_text = re.sub("\[[0-9]+\]", "", item_text)

    # Triage them using re
    if re.match(r"[AD_|BC_]?[0-9]+\s.+", item_text):
        if item_text == THRESHOLD:
            break

        item_text = re.sub(r"([0-9]+)[\s]+[\-|\–][\s]+(.+)", decapitalize, item_text)
        if len(item_text) >= LIMIT_TWEET:
            print("Event has more than {} chars: {}".format(LIMIT_TWEET, len(item_text)))
            continue
        triaged_items.append(item_text)

if len(triaged_items) > 0:
    selected = triaged_items[randint(0, len(triaged_items)-1)]
    print(post_tweet(selected))
    print(selected)