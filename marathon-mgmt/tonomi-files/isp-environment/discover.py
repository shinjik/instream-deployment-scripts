#!/usr/bin/env python3

import sys
import yaml

import marathon_comm


arguments = yaml.safe_load(sys.stdin)

marathon_url = arguments.get('configuration', {}).get('configuration.marathonURL', 'http://localhost:8080')

apps = marathon_comm.list_apps(marathon_url, {})
env_ids = []
for app in apps:
    eid = app.marathon_model.get('labels',{}).get('_tonomi_environment')
    if eid and eid not in env_ids:
        env_ids.append(eid)

def get_tonomi_model(eid):
    if eid:
        return {
            'name': eid,
            'interfaces': {
                'info': {
                    'signals': {
                        'app-id': eid
                    }
                }
            }
        }
    else:
        return {}

result = {
    'instances': { eid: get_tonomi_model(eid) for eid in env_ids }
}
yaml.safe_dump(result, sys.stdout)
