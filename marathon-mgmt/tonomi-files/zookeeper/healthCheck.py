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
                'failed': app._model['tasksUnhealthy'] > 0 #bool(vm.model.get('failure'))
            }
        }
        
        
        port_mappings = {str(p['containerPort']): str(p['servicePort']) for p in app.marathon_model['container']['docker']['portMappings']}
        interfaces = {
            
            'compute': {
                'signals': {
                    'ram': app._model['mem'],
                    'cpu': app._model['cpus'],
                    'disk': app._model['disk'],
                    'instances': app._model['instances'],
                    #'portMappings': port_mappings
                }
            },
            
            'zookeeper': {
                'signals': {
                    'lbPort': str(port_mappings['2181'])
                }  
            }
        }

        components = multidict()
        components['zk'] = {
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
        # a vm is absent, set its status to destroyed
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
