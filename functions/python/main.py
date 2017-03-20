import json
import logging
import os
import re

import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handle(event, context):
    """
    Lambda handler
    """

    if not os.environ["REFRESH_TOKEN"] or not os.environ["CLIENT_SECRET"]:
        return "please set REFRESH_TOKEN and CLIENT_SECRET"

    access_token = get_access_token()
    logger.info("access_token: %s", access_token)

    user_id = get_user_id(access_token)
    logger.info("user_id: %s", user_id)

    items = get_items(user_id, access_token)
    logger.info("item count: %s", len(items))

    # get advertise
    advertise_ids = get_adviertise_ids(items)
    logger.info("advertise ids: %s", len(advertise_ids))

    # get duplicate
    duplicate_ids = get_duplicate_ids(items)
    logger.info("duplicate ids: %s", len(duplicate_ids))

    mark = advertise_ids.copy()
    mark.update(duplicate_ids)
    if len(mark) > 0:
        mark_entries(mark, access_token)

    return {}

def get_access_token():
    url = "https://cloud.feedly.com/v3/auth/token"
    resp = requests.post(url, data={
        "refresh_token": os.environ["REFRESH_TOKEN"],
        "client_id": "feedly",
        "client_secret": os.environ["CLIENT_SECRET"],
        "grant_type": "refresh_token"
    })
    return resp.json()["access_token"]

def get_user_id(access_token):
    url = "https://cloud.feedly.com/v3/profile"
    resp = requests.get(url, headers={
        "Authorization": "Bearer " + access_token
    })
    return resp.json()["id"]

def get_items(user_id, access_token):
    url = "https://cloud.feedly.com/v3/streams/contents?streamId=user/"\
    + user_id + "/category/global.all&count=1000&unreadOnly=true"
    resp = requests.get(url, headers={
        "Authorization": "Bearer " + access_token
    })
    items = resp.json()["items"]
    items.reverse()
    return items

def get_adviertise_ids(items):
    ids = set([])
    for i in items:
        if i["title"] and re.compile("^((PR:)|(AD:)|(\\[PR\\])).*").match(i["title"].upper()):
            logger.info("advertise item : %s", i["title"])
            ids.add(i["id"])
    return ids

def get_duplicate_ids(items):
    ids = set([])
    urls = set([])
    for i in items:
        alternate = i["alternate"]
        if not alternate or len(alternate) == 0:
            continue
        url = alternate[0]["href"]
        if url in urls:
            logger.info("duplicate item : %s %s", i["title"], url)
            ids.add(i["id"])
        else:
            urls.add(url)
    return ids

def mark_entries(ids, access_token):
    url = "https://cloud.feedly.com/v3/markers"
    resp = requests.post(url, headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token
    }, data=json.dumps({
        "type": "entries",
        "action": "markAsRead",
        "entryIds": list(ids)
    }))
    logger.info("mark entities : %s", resp.text)
