#!/usr/bin/env python3
"""
homeexchangeradar.py

Checks your saved HomeExchange searches (fetched from a public GitHub-hosted
searches.json) against HomeExchange's search API and notifies you via
Telegram when a new listing shows up for one of them.

All secrets (Telegram bot token/chat id, HomeExchange session cookie, the
calendar API bearer token) and the local notification-history path live in a
local secrets.json next to this script -- never in this file, never in git.
See secrets.example.json for the shape.

TODO Search for non reciprocal also
TODO Calendar check
"""

import json
import os
import sys
from datetime import datetime

import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SECRETS_PATH = os.environ.get("HOMEEXCHANGERADAR_SECRETS", os.path.join(SCRIPT_DIR, "secrets.json"))


def load_secrets(path):
    if not os.path.exists(path):
        sys.exit(
            f"secrets.json not found at {path}.\n"
            "Copy secrets.example.json to secrets.json next to this script "
            "and fill in your real values first."
        )
    with open(path) as f:
        return json.load(f)


def build_home_exchange_headers(secrets):
    return {
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Accept-Language': 'en',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Origin': 'https://www.homeexchange.com',
        'Referer': 'https://www.homeexchange.com/search-v2/everywhere',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.4 Safari/605.1.15',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'X-LEGACY-RESPONSE': 'false',
        'X-HE-PAGE-NAME': 'SEARCH_PAGE',
        'he_web_version': '20.5.0',
        'X-SEARCH-API-VERSION': 'v2',
        'Cookie': secrets['home_exchange_cookie'],
    }


def load_notification_history(path):
    with open(path, 'r') as f:
        return json.load(f)


def save_notification_history(path, data):
    with open(path, 'w') as f:
        json.dump(data, f)


def check_exchanges(search, secrets, headers, notified_flag):
    url = "https://bff.homeexchange.com/search/homes?offset=0&limit=100"
    payload = {
        "search_query": {
            "location": {
                "bounds": search["bounds"]
            },
            "availability": {
                "date_range": {
                    "from": search["from"],
                    "to": search["to"]
                },
                "reciprocal": False
            },
            "home": {
                "is_private_room": False,
                "size": {
                    "beds": {
                        "adults": 1
                    }
                }
            },
            "extended": False
        }
    }

    try:
        flexibility = int(search.get("flexibility", 0))
    except Exception:
        flexibility = 0
    if flexibility > 0:
        payload["search_query"]["calendar"] = {"flexibility": flexibility}

    payload = json.loads(json.dumps(payload))
    if search["from"] == "":
        del payload["search_query"]["availability"]["date_range"]

    try:
        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=15)
    except requests.RequestException:
        return

    content_type = resp.headers.get('Content-Type', '')
    if resp.status_code != 200:
        return
    if 'application/json' not in content_type.lower():
        return

    try:
        homes = resp.json()
    except ValueError:
        return

    json_data = load_notification_history(secrets['notification_history_file'])

    homes_list = homes.get("homes") if isinstance(homes, dict) else None
    if not homes_list:
        return

    for x in homes_list:
        home_id = x.get("homeId") or x.get("id")
        known_ids = json_data["homes"].get(search["name"], [])
        if home_id not in known_ids:
            notify_new_home(home_id, search, secrets, notified_flag)


def add_id_to_history(secrets, search_name, id_to_add):
    json_data = load_notification_history(secrets['notification_history_file'])
    ids_array = json_data["homes"].get(search_name, [])
    if id_to_add not in ids_array:
        ids_array.append(id_to_add)
        json_data["homes"][search_name] = ids_array
        save_notification_history(secrets['notification_history_file'], json_data)


def add_calendar_to_history(secrets, search_name, id_to_add):
    json_data = load_notification_history(secrets['notification_history_file'])
    ids_array = json_data["calendars"].get(search_name, [])
    if id_to_add not in ids_array:
        ids_array.append(id_to_add)
        json_data["calendars"][search_name] = ids_array
        save_notification_history(secrets['notification_history_file'], json_data)


def notify_new_home(home_id, search, secrets, notified_flag):
    if home_id is None:
        return
    notified_flag["value"] = True
    message = f"New home found for your search {search['name']} https://www.homeexchange.com/homes/view/{home_id}"
    notification_url = (
        f"https://api.telegram.org/bot{secrets['telegram_token']}/sendMessage"
        f"?chat_id={secrets['telegram_chat_id']}&text={message}"
    )
    try:
        requests.get(notification_url)
    except Exception:
        pass
    print(message)
    add_id_to_history(secrets, search['name'], home_id)


def check_calendar(home_id, secrets):
    url_calendar = f"https://api.homeexchange.com/v1/homes/{home_id}/calendar"
    headers_calendar = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Authorization': f"Bearer {secrets['home_exchange_calendar_bearer_token']}",
        'Sec-Fetch-Site': 'same-site',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en',
        'Sec-Fetch-Mode': 'cors',
        'Host': 'api.homeexchange.com',
        'Origin': 'https://www.homeexchange.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Referer': 'https://www.homeexchange.com/',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
    }
    response_calendar = requests.get(url_calendar, headers=headers_calendar, timeout=15)
    return response_calendar.text


def main():
    secrets = load_secrets(SECRETS_PATH)

    response = requests.get(secrets['configuration_url'], timeout=15)
    if response.status_code != 200:
        sys.exit(1)

    searches = json.loads(response.text)
    headers = build_home_exchange_headers(secrets)
    notified_flag = {"value": False}

    for search in searches:
        if search.get("active") is True:
            check_exchanges(search, secrets, headers, notified_flag)

    if not notified_flag["value"]:
        now = datetime.now()
        if now.hour == 22:
            message = f"No new Exchanges found at {now.strftime('%H:%M:%S')}"
            notification_url = (
                f"https://api.telegram.org/bot{secrets['telegram_token']}/sendMessage"
                f"?chat_id={secrets['telegram_chat_id']}&text={message}&disable_notification=true"
            )
            try:
                requests.get(notification_url)
            except Exception:
                pass


if __name__ == "__main__":
    main()
