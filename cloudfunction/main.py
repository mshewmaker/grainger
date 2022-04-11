#!/usr/bin/python3

import sys
import csv

from flask import escape
import functions_framework

def get_states():
    states={}
    with open('states.csv',newline='') as csvfile:
        csvreader= csv.reader(csvfile)
        for row in csvreader:
            if csvreader.line_num != 1:
                if len(row)==2:
                    states[row[1].upper()]=row[0]
                else:
                    print("Bad line number %d in csv file" % (csvreader.line_num,),file=sys.stderr)
                    sys.exit(1)
    return(states)

states=get_states()

@functions_framework.http
def process_request(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """

    path=request.path
    path=path.strip('/')
    state_code=path.split('/')[-1].upper()
    if state_code in states:
        return escape(states[state_code]+'\n'),200
    elif state_code == '':
        return "Missing state code\n",404
    else:
        return "Unrecognized state code\n",404
