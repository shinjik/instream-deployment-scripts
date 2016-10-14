#!/usr/bin/env python3

import sys
import yaml

import marathon_comm



from collections import defaultdict
from yaml.representer import SafeRepresenter

# to serialize defaultdicts normally
SafeRepresenter.add_representer(defaultdict, SafeRepresenter.represent_dict)

arguments = yaml.safe_load(sys.stdin)

app_ids = list(arguments.get('instances', {}).keys())
marathon_url = arguments.get('configuration', {}).get('configuration.marathonURL', 'http://localhost:8080')

def multidict():
    return defaultdict(multidict)


app_infos = {}
for appid in app_ids:
    app = marathon_comm.info(marathon_url, appid)
    if app:
        status = {
            'flags': {
                'active': True,
                'converging': False,
                'failed': app.marathon_model['tasksUnhealthy'] > 0 #bool(vm.model.get('failure'))
            }
        }
        
        
        port_mappings = {str(p['containerPort']): str(p['servicePort']) for p in app.marathon_model['container']['docker']['portMappings']}
        interfaces = {
            
            'compute': {
                'signals': {
                    'ram': app.marathon_model['mem'],
                    'cpu': app.marathon_model['cpus'],
                    'disk': app.marathon_model['disk'],
                    'instances': app.marathon_model['instances'],
                    #'portMappings': port_mappings
                }
            },
            
            'ui': {
                'signals': {
                    'lbPort': str(port_mappings['3000'])
                }
            }
        }

        components = multidict()
        components['ui'] = {
            'reference': {
                'mapping': 'apps.app-by-id',
                'key': app.id
            }
        }
        
        
        app_infos[appid] = {
            'instanceId': app.id,
            'name': app.id,
            'status': status,
            'interfaces': interfaces,
            'components': components,
        }

        
    else:
        # set status to destroyed
        app_infos[appid] = {
            'status': {
                'flags': {
                    'active': False,
                    'converging': False,
                    'failed': False
                }
            }
        }

result = {
    'instances': app_infos
}
yaml.safe_dump(result, sys.stdout)
