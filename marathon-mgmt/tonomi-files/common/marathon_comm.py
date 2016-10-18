#!/usr/bin/env python3

import sys
import yaml
import datetime
import requests
import json


class MarathonApp:
    marathon_model = {}

    def __init__(self, model):
        self.marathon_model = model

    @property
    def id(self):
        return self.marathon_model.get('id')

    @id.setter
    def id(self, value):
        self.marathon_model['id'] = value



    def __str__(self):
        return "MarathonApp({})".format(self.id)

    def __repr__(self):
        return str(self)




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


def list_apps(url, filters={}):
    res = get_json(url + "/v2/apps")
    result = res.get('apps', [])
    if filters:
        for k in list(filters.keys()):
            result = filter(lambda x: x.get('labels', {}).get(k, None) == filters[k], result)

    return map(lambda x: MarathonApp(x), result)

def info(url, app_id):
    res = None
    try:
        res = make_request('GET', url + "/v2/apps" + app_id)
        return MarathonApp(res['app'])
    except Exception:
        return None

def get_app_info(url, app_id):
    res = None
    try:
        res = make_request('GET', url + "/v2/apps" + app_id)
        return res['app']
    except Exception:
        return None

def destroy(url, app_id):
    res = make_request('DELETE', url + "/v2/apps" + app_id)

def restart(url, app_id):
    post_json(url + "/v2/apps" + app_id + '/restart')

def scale(url, app_id, instances):
    cmd = {'instances': instances}
    make_request('PUT', url + "/v2/apps" + app_id, json.dumps(cmd))

def create(url, configuration):
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
    if configuration.get('configuration.disk', None):
        app_definition['disk'] = configuration['configuration.disk']
    if configuration.get('configuration.labels', None):
        app_definition['labels'] = configuration['configuration.labels']
    if configuration.get('configuration.env', None):
        app_definition['env'] = configuration['configuration.env']
    if configuration.get('configuration.constraints', None):
        app_definition['constraints'] = configuration['configuration.constraints']
    if configuration.get('configuration.cmd', None):
        app_definition['cmd'] = configuration['configuration.cmd']
    if configuration.get('volumes', None):
        app_definition['container']['volumes'] = configuration['volumes']
    if configuration.get('residency', None):
        app_definition['container']['residency'] = configuration['residency']
    if configuration.get('fetch', None):
        app_definition['fetch'] = configuration['fetch']


    res = make_request('POST', url + "/v2/apps", json.dumps(app_definition))
    if res.get('message', None):

        print("Error: " + str(res), file=sys.stderr)
        raise RuntimeError

def update(url, app_id, app_definition):
    res = make_request('PUT', url + "/v2/apps" + app_id, json.dumps(app_definition))
    if res.get('message', None):

        print("Error: " + str(res), file=sys.stderr)
        raise RuntimeError