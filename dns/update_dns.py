#!/usr/bin/python3

import sys
import csv
import os
from flask import Flask
import requests
import json

from config import *
#
# The above import sets these variables:
#
#CLOUDFLARE_API_TOKEN=
#CLOUDFLARE_ZONE_ID=
#CLOUDFLARE_ACCOUNT_ID=
#ZONE_NAME=

HEADERS = {"Authorization": "Bearer " + CLOUDFLARE_API_TOKEN,
           "Content-type":  "application/json"}

base_api_url= "https://api.cloudflare.com/client/v4/"

verify_url       = base_api_url + "user/tokens/verify"
zone_records_url = base_api_url + "zones/" + CLOUDFLARE_ZONE_ID + "/dns_records"

full_subdomain="dns."+ZONE_NAME

def update_dns(states):
    #
    # Get all TXT records in zone
    #
    r=requests.get(zone_records_url, headers=HEADERS, params={"type": "TXT", "per_page": "5000", "match": "all"})
    response=r.json()
    if response["success"] != True:
        print("DNS query failed",file=sys.stderr)
        exit(1)
    #
    # Find all TXT records responses that are in the target zone.
    #
    # Put this list of responses into in_zone_entries, except if:
    #
    #  1. fqdn is a duplicate key entry, or 
    #  2. the "two letter" subdomain key doesn't appear in states
    #
    # don't put in in_zone_entries, and delete the corresponding
    # dns entry.
    #
    in_zone_entries=[]
    seen=[]
    for result in response["result"]:
        if result["name"].endswith(".dns."+ZONE_NAME):
            two_letter=result["name"][:-len(".dns."+ZONE_NAME)].upper()
            if two_letter in seen or two_letter not in states:
                # Delete extraneous or duplicate two_letter codes
                r=requests.delete(zone_records_url + '/' + result['id'], headers=HEADERS,)
            else:
                # Keep track of the fact that we've seen this response.
                in_zone_entries.append(result)
                seen.append(two_letter)

    #
    # Add missing states
    #
    for two_letter in set(states) - set(seen):
        r=requests.post(zone_records_url, headers=HEADERS, json={"type": "TXT", "name": two_letter+".dns", "content":states[two_letter], "ttl": 60,"Authorization": "Bearer " + CLOUDFLARE_API_TOKEN,"Content-Type":  "application/json"})
        response=r.json()

    #
    # Update incorrect states:
    #
    # For instance, if someone corrects a misspelling of a state in the states.csv file.
    #
    # Note: Cloudflare doesn't allow dulicate key+value combonations,
    #       so updates have to be done only after duplicate keys are
    #       deleted
    #
    for result in in_zone_entries:
        two_letter=result["name"][:-len(".dns."+ZONE_NAME)].upper()
        if result["content"]!=states[two_letter]:
            # Update this two-letter's key's value
            r=requests.put(zone_records_url + '/' + result['id'], headers=HEADERS, json={"type": "TXT", "name": two_letter+".dns", "content":states[two_letter], "ttl": 60,"Authorization": "Bearer " + CLOUDFLARE_API_TOKEN,"Content-Type":  "application/json"})
            response=r.json()
            #print(json.dumps(r.json(),indent=4))

def get_states():
    states={}
    with open('states.csv',newline='') as csvfile:
        csvreader= csv.reader(csvfile)
        for row in csvreader:
            if csvreader.line_num != 1:
                if len(row)==2:
                    states[row[1].upper()]=row[0]
                else:
                    print("Bad line number %d in csv file has these fields: %s" % (csvreader.line_num,row),file=sys.stderr)
                    sys.exit(1)
    return(states)

def main():
    states=get_states()
    update_dns(states)


if __name__ == "__main__":
    main()
