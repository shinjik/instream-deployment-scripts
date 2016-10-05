#!/usr/bin/env python3

import sys
import json
import requests
import yaml


def get_json(url):
    r = requests.get(url)
    return r.json()

def post_json(url, data=None):
    r = requests.post(url, data)
    return r.json()

def make_request(method, url, data=None):
    if data:
        r = requests.request(method, url, data=data)
    else:
        r = requests.request(method, url)
    if r.json():
        return r.json()
    else:
        raise RuntimeError

def list_apps(url):
    res = get_json(url + "/v2/apps")
    return res.get('apps', [])


arguments = yaml.safe_load(sys.stdin)
yaml.safe_dump(arguments, sys.stderr)
marathon_url = arguments.get('configuration', {}).get('configuration.marathonURL', 'http://localhost:8080')
app_ids = list(arguments.get('instances', {}).keys())

instance_results = {}

for app in app_ids:
    command_id = list(arguments.get('instances', {}).get(app).get('commands').keys())[0]
    instances = arguments.get('instances', {}).get(app).get('commands').get(command_id).get('control').get('scale').get('instances')
    #res = post_json(marathon_url + "/v2/apps" + app + '/restart')
    cmd = {'instances': instances}
    res = make_request('PUT', marathon_url + "/v2/apps" + app, json.dumps(cmd))
    instance_results[app] = {
        '$pushAll': {
            'commands.'+command_id: [
                {'$intermediate': True}, { 'status.flags.converging': True }
                #{'signals.status.flags.converging': True, 'status.flags.active': False, 'instances.status.flags.active': False, 'instances.status.flags.converging': True, 'signals.instances.tasks'
                ]
            },
        '$set': {
            'status.flags.converging': True,
            'status.flags.active': False,
        #       'instances.tasks': []
            }
    }






result = {
    'instances': instance_results
}

yaml.safe_dump(result, sys.stdout)
