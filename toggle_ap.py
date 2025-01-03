import requests
import json
from datetime import datetime
from requests_toolbelt.utils import dump
import urllib3

urllib3.disable_warnings()

def startSession(config):
    base_url    = config['base_url']
    username    = config['username']  
    password    = config['password']
    login_url   = base_url + '/api/auth/login'
    
    # create a custom requests object, modifying the global module throws an error
    session = requests.Session()
    session.verify = False  # Disable SSL verification (if using self-signed certs)

    assert_status_hook = lambda response, *args, **kwargs: response.raise_for_status()
    session.hooks["response"] = [assert_status_hook]

    # dump verbose request and response data to stdout
    def logging_hook(response, *args, **kwargs):
        data = dump.dump_all(response)
        # print(data.decode('utf-8'))

    #setup Requests to log request and response to stdout verbosely
    session = requests.Session()
    session.verify = False  # Disable SSL verification (if using self-signed certs)
    session.hooks["response"] = [logging_hook]

    # set required headers
    session.headers.update({
        "Content-Type": "application/json; charset=utf-8"
    })    

    creds = json.dumps({'username': username,'password': password})
    response = session.post(login_url, data=creds)
    # new API requires the CSRF token going forward else we get 401's or 404's
    session.headers.update({
        "X-CSRF-Token": response.headers['X-CSRF-Token']
        })
    
    return session

def closeSession(config, session):
    base_url    = config['base_url']
    username    = config['username']  
    password    = config['password']
    logout_url  = base_url + '/api/auth/logout'
    
    creds = json.dumps({'username': username,'password': password})

    # close session
    response = session.post(logout_url, data=creds)
    return response

def getDeviceId(config, session, ap):
    # UniFi Controller Details
    base_url    = config['base_url']
    username    = config['username']  
    password    = config['password']
    site_id     = config['site_id']  
        
    response = session.get(f"{base_url}/proxy/network/api/s/{site_id}/stat/device")
    devices = response.json()["data"]
    for device in devices:
        if device['name'] == ap:
            return device['device_id']
    return None

def toggleAP(config, ap, action):
    base_url    = config['base_url']
    site_id     = config['site_id']  
    session     = startSession(config)      
    ap_id       = getDeviceId(config, session, ap)  
    ap_url      = base_url + '/proxy/network/api/s/' + site_id + '/rest/device/' + ap_id
    
    state = True  if action == 'off' else False
    mode  = 'off' if action == 'off' else 'high'
    
    # set powermode to low 
    payload = json.dumps({'tx_power_mode': mode})
    response_1  = session.put(ap_url, data = payload)
    
    # playload = json.dumps({
    #         "radio_schedules": [
    #         {
    #         "radio": "ng",  
    #         "start_time": "08:00",
    #         "end_time": "18:00"
    #         },
    #         {
    #         "radio": "na",  
    #         "start_time": "09:00",
    #         "end_time": "17:00"
    #         }
    #     ]
    # })
    # response_3  = session.put(ap_url, data = payload)

    
    # turn off
    payload = json.dumps({'disabled': state})
    response_2  = session.put(ap_url, data = payload)
    if response_1.status_code == 200 and response_2.status_code == 200:
        print(f"AP {ap} is now in power mode {mode} and turned {action}.")
    elif response_1.status_code != 200: 
        print(f"Failed to toggle AP {ap} to power mode: {mode}. Status code: {response_1.status_code}.")
    elif response_2.status_code != 200: 
        print(f"Failed to toggle AP {ap} {action} and to power mode {mode}. Status code: {response_1.status_code}.")
    
    closeSession(config, session)

