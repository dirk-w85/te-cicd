#!/usr/bin/env python3
# -*- coding: UTF-8 -*-# enable debugging
print ("""
Copyright (c) 2021 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at

             https://developer.cisco.com/docs/licenses
               
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
""")
__author__ = "Dirk Woellhaf <dwoellha@cisco.com>"
__contributors__ = [
    "Dirk Woellhaf <dwoellha@cisco.com>"
]
__copyright__ = "Copyright (c) 2023 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"


import json
import requests
import sys
import logging
import time
from datetime import datetime


def te_create_instant_test(Settings, DeployCount):

    url = "https://api.thousandeyes.com/v6/instant/page-load"

    payload = { 
        "agents": [ 
            {"agentId": 4844}
            ], 
        "testName": "Website Deployment - Change #"+str(DeployCount), 
        "url": Settings["teTarget"]
    }

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+Settings["teToken"]
    }

    response = requests.request("POST", url, headers=headers, data = json.dumps(payload))

    if response.status_code >= 300:
        print("Failed GET response {} {}".format(response.status_code, response.json()))
        logging.error("Failed POST response {} {}".format(response.status_code, response.json()))
    elif response.status_code == 201:
        InstatTestData = json.loads(response.text)
        StateMsg= "Instant Test created with ID "+str(InstatTestData["test"][0]["testId"])+"\nLink: https://app.thousandeyes.com/view/tests/?testId="+str(InstatTestData["test"][0]["testId"])
        print(StateMsg)
        return InstatTestData["test"][0]["testId"]

def check_instant_test(Settings, teTestId):   
    gotResults = 0
    #time.sleep(30) 
    url = "https://api.thousandeyes.com/v6/web/page-load/"+str(teTestId)+".json"

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+Settings["teToken"]
    }

    while gotResults == 0:
        print("Waiting for Test Results...")
        response = requests.request("GET", url, headers=headers)

        if response.status_code >= 300:
            print("Failed GET response {} {}".format(response.status_code, response.json()))
            logging.error("Failed POST response {} {}".format(response.status_code, response.json()))
        elif response.status_code == 200:
            InstantTestResults = json.loads(response.text)
            if "pageLoad" in InstantTestResults["web"]:
                gotResults = 1
        time.sleep(5)
    
    Results = {}
    Results["teTestId"] = teTestId
    Results["teInstant"] = InstantTestResults["web"]["pageLoad"][0]
    
    if Settings["type"] == "pre":
        f = open("pre.json", "w")
        f.write(json.dumps(Results))
        f.close()



def main():
  Settings={}
  Settings["teToken"] = sys.argv[1]
  Settings["type"]= sys.argv[2] #pre or post
  Settings["teTarget"] = sys.argv[3]
  
  print("-"*20)

  print("Step: "+Settings["type"].upper()+" Deployment" )
  check_instant_test(Settings, te_create_instant_test(Settings, 1))
 
  print("-"*20)

if __name__ == "__main__":    
    main()