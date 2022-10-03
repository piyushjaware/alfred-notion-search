import json
import sys
from typing import List
from urllib.parse import urlparse

import requests

TOKEN = 'your Notion Integration token'


# This logs to alfred debug console without affecting std output that Alfred uses to read response
def log(*args):
    print(args, file=sys.stderr)


# query paarm is optional
def parse_query_param():
    q = ""
    if len(sys.argv) > 1:
        q = sys.argv[1]
    log(f"Searching for '{q}'")
    return q


def search_notion(q: str):
    url = 'https://api.notion.com/v1/search'
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {TOKEN}",
        "Notion-Version": "2022-06-28"}

    payload = {
        "query": q,
        "filter": {
            "value": "page",
            "property": "object"
        },
        "page_size": 10
    }
    response = requests.request("POST", url, json=payload, headers=headers)
    if response.status_code != 200:
        log("Error occurred while fetching notion results",
            response.status_code, response.text)
        raise Exception
    return response.json().get("results")


def map_results_to_alfred_items(results: List):
    items = []
    for r in results:
        item = map(r)
        items.append(item)
    return items


def map(result: str):
    title = result['properties']['title']['title'][0]['plain_text']
    url = get_desktop_client_link(result)
    emoji = read_emoji(result)
    return {
        "title": f"{emoji} {title}",
        "arg": url,
        "autocomplete": title
    }


def get_desktop_client_link(result):
    u = urlparse(result['url'])
    u = u._replace(scheme='notion').geturl()
    return u


def read_emoji(result):
    emoji = ''
    # emoji is an optional prop
    if result.get('icon') and result['icon']['type'] == 'emoji':
        emoji = result['icon']['emoji']
    return emoji


def send_response(items: List):
    alfred_json = json.dumps({"items": items})
    sys.stdout.write(alfred_json)


def main():
    q = parse_query_param()
    results = search_notion(q)
    filter_items = map_results_to_alfred_items(results)
    send_response(filter_items)


if __name__ == "__main__":
    main()
