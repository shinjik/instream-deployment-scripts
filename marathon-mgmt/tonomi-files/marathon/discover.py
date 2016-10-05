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

marathon_url = arguments.get('configuration', {}).get('configuration.marathonURL', 'http://localhost:8080')

apps = list_apps(marathon_url)

def get_tonomi_model(app):
    if app['id']:
        return {
            'name': app['id'],
            'interfaces': {
                'info': {
                    'signals': {
                        'app-id': app['id']
                    }
                }
            }
        }
    else:
        return {}

result = {
    'instances': { app['id']: get_tonomi_model(app) for app in apps }
}
yaml.safe_dump(result, sys.stdout)
