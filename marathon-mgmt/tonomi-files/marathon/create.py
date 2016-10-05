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
#yaml.safe_dump(arguments, sys.stderr)
marathon_url = arguments.get('configuration', {}).get('configuration.marathonURL', 'http://localhost:8080')
app_ids = list(arguments.get('launch-instances', {}).keys())

instance_results = {}

for app in app_ids:
    #command_id = list(arguments.get('instances', {}).get(app).get('commands').keys())[0]
    configuration = arguments.get('launch-instances').get(app).get('configuration')

    portMappings = []
    for p in configuration['configuration.portMappings']:
        portMappings.append(
            {
                "containerPort": int(list(p.keys())[0]),
                "hostPort": 0,
                "servicePort": int(p[list(p.keys())[0]]),
                "protocol": "tcp"
            
            })
        
    app_definition = {
        "id": configuration['configuration.name'],
        "cpus": float(configuration['configuration.cpu']),
        "mem": configuration['configuration.ram'],
        "disk": configuration['configuration.disk'],
        
        "instances": configuration['configuration.instances'],
        "container": {
            "type": "DOCKER",
            "docker": {
                "image": configuration['configuration.imageId'],
                "network": "BRIDGE",
                "portMappings": portMappings
                
            }
        }
    }
    res = make_request('POST', marathon_url + "/v2/apps", json.dumps(app_definition))
    if res.get('message', None):

        print("Error: " + str(res), file=sys.stderr)
        sys.exit(1)
    #res =  make_request('DELETE', marathon_url + "/v2/apps" + app)
    instance_results[configuration['configuration.name']] = {
        'instanceId': app,

        # '$pushAll': {
        #     'commands.'+command_id: [
        #         {'$intermediate': True}, { 'status.flags.converging': True }
        #         #{'signals.status.flags.converging': True, 'status.flags.active': False, 'instances.status.flags.active': False, 'instances.status.flags.converging': True, 'signals.instances.tasks'
        #         ]
        #     },
        '$set': {
            'status.flags.converging': True,
            'status.flags.active': False  
           }
    }


#sys.exit(1)



result = {
    'instances': instance_results
}

yaml.safe_dump(result, sys.stdout)
