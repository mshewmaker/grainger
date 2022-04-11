#!/usr/bin/python3

import sys
import csv
from flask import Flask

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

app = Flask(__name__)

@app.route('/state/<state_code>/')
def lookup(state_code):
    if state_code.upper() in states:
        return(states[state_code.upper()] + '\n',200)
    else:
        return('Unrecognized state code\n',404)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT",8080)))
    main()
