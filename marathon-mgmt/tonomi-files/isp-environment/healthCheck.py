#!/usr/bin/env python3

import sys
import yaml

import marathon_comm
from model import InstreamEnvironment



from collections import defaultdict
from yaml.representer import SafeRepresenter

# to serialize defaultdicts normally
SafeRepresenter.add_representer(defaultdict, SafeRepresenter.represent_dict)

arguments = yaml.safe_load(sys.stdin)

env_ids = list(arguments.get('instances', {}).keys())
marathon_url = arguments.get('configuration', {}).get('configuration.marathonURL', 'http://localhost:8080')

def multidict():
    return defaultdict(multidict)


env_infos = {}
for envid in env_ids:
    env = InstreamEnvironment(marathon_url)
    env.load(envid)


    


    if env:
        status = {
            'flags': {
                'active': True,
                'converging': False,
                'failed': False
                #'failed': app.marathon_model['tasksUnhealthy'] > 0 #bool(vm.model.get('failure'))
            }
        }
        
        zk = env.get_apps_by_type('zookeeper')[0]
        redis = env.get_apps_by_type('redis')[0]

        interfaces = {
            'entrypoint': {
                'signals': {
                    'URL': "http://nonexistent"
                    
                }  
            }
        }
        components = multidict()

        for app in env.applications:
            interfaces[app.type] = {
                'signals': app.get_info()
            }
            components[app.type] = {
                'reference': {
                    'mapping': app.type + '.' + app.type + '-by-id',
                    'key': app.id
                }
            }
        

        
        
        env_infos[envid] = {
            'instanceId': env.id,
            'name': env.id,
            'status': status,
            'interfaces': interfaces,
            'components': components,
        }

    else:
        # env is absent, set its status to destroyed
        env_infos[envid] = {
            'status': {
                'flags': {
                    'active': False,
                    'converging': False,
                    'failed': False
                }
            }
        }

result = {
    'instances': env_infos
}
yaml.safe_dump(result, sys.stdout)
