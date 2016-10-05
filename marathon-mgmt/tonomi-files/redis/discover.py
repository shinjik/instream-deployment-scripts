#!/usr/bin/env python3

import sys
import yaml

import marathon_comm


arguments = yaml.safe_load(sys.stdin)

marathon_url = arguments.get('configuration', {}).get('configuration.marathonURL', 'http://localhost:8080')

apps = marathon_comm.list_apps(marathon_url, {'_tonomi_application': 'redis'})

def get_tonomi_model(app):
    if app.id:
        return {
            'name': app.id,
            'interfaces': {
                'info': {
                    'signals': {
                        'app-id': app.id
                    }
                }
            }
        }
    else:
        return {}

result = {
    'instances': { app.id: get_tonomi_model(app) for app in apps }
}
yaml.safe_dump(result, sys.stdout)
