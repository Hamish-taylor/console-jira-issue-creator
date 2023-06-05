import requests
from requests.auth import HTTPBasicAuth
import json

base_url = "https://hamisht.atlassian.net"

issue_url = "/rest/api/3/issue"

issue_types_url = "/rest/api/3/issuetype"

fields_url = "/rest/api/3/field"

fieldKey = ""
fields_options = "/rest/api/3/field/"

auth = HTTPBasicAuth("hamisht11@gmail.com", "ATATT3xFfGF07BEVGMceqQvG07jVsOlr-Lsfgz06iW2b9aTrDKN0lEKT-wO4XKbGKC7luPZyspWPu3He9J0FMIuLLF9v1I4SDq6cNU_AFjao-Yj-NjV_HQXppL9fggMaAGVdN0Z99rnjrUY09I6YDW71rrk3qBRjwBJBqJiZU8S5bhz3Vrjz4FA=7963CA37")

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# issue types
response = requests.request(
    "GET",
    base_url+issue_types_url,
    headers=headers,
    auth=auth,
)

for i in json.loads(response.text):
    print("Name: " + i["name"])
    print("Description: " + i["description"])
    print("Id: "+i["id"])
    print("\n")

# fields
response = requests.request(
    "GET",
    base_url+fields_url,
    headers=headers,
    auth=auth,
)
for i in json.loads(response.text):
    if i["name"] == "Work type":
        print(json.dumps(i,
                         sort_keys=True, indent=4, separators=(",", ": ")))
        print("Name: " + i["name"])
        print("Id: " + i["id"])
        print("Key: " + i["key"])
        print("Id: " + i["id"])
        print("\n")
        fieldKey = i["key"]


# field options
response = requests.request(
    "GET",
    base_url+fields_options + fieldKey + "/option",
    headers=headers,
    auth=auth,
)
print("-----fields-----")
print(json.dumps(json.loads(response.text),
      sort_keys=True, indent=4, separators=(",", ": ")))
for i in json.loads(response.text):
    print(json.dumps(i,
                     sort_keys=True, indent=4, separators=(",", ": ")))
    print("\n")


payload = json.dumps({
    "fields": {
        "assignee": {
            "id": "5ed8fed33d527a0ac3a7615b"
        },
        "reporter": {
            "id": "5ed8fed33d527a0ac3a7615b"
        },
        "description": {
            "content": [
                {
                    "content": [
                        {
                            "text": "Order entry fails when selecting supplier.",
                            "type": "text"
                        }
                    ],
                    "type": "paragraph"
                }
            ],
            "type": "doc",
            "version": 1
        },
        "customfield_10034": {
            "id": "10018"
        },
        "issuetype": {
            "id": "10001"
        },
        "labels": [
            "bugfix",
            "blitz_test"
        ],
        "project": {
            "id": "10000"
        },
        "summary": "Main order flow broken",
    },
    "update": {}
})

response = requests.request(
    "POST",
    base_url+issue_url,
    data=payload,
    headers=headers,
    auth=auth
)
print(json.dumps(json.loads(response.text),
      sort_keys=True, indent=4, separators=(",", ": ")))
