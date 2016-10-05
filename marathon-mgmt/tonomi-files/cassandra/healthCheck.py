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
                    #'instances': app.marathon_model['instances'],
                    #'portMappings': port_mappings
                }
            },
            
            'cassandra': {
                'nativePort': str(port_mappings['9042']),
                'thriftPort': str(port_mappings['9160'])
            }
        }

        components = multidict()
        components['cassandra-standalone'] = {
            'reference': {
                'mapping': 'apps.app-by-id',
                'key': app.id
            }
        }
        # if 'volumes' in vm.model:
        #     for volid in vm.model['volumes']:
        #         vol = fvol.load(volid)
        #         color = vol.color if vol else 'unknown'
        #         components[color]['components'][volid] = {
        #             'reference': {
        #                 'mapping': 'volumes.volume-by-id',
        #                 'key': volid
        #             }
        #         }
        
        app_infos[appid] = {
            'instanceId': app.id,
            'name': app.id,
            'status': status,
            'interfaces': interfaces,
            'components': components,
        }

        # entries = []
        # if 'tasks' in vm.model:
        #     remaining_tasks = []
        #     for task in vm.model['tasks']:
        #         if task['timestamp'] <= datetime.datetime.utcnow().timestamp():
        #             entries.append({
        #                 'severity': 'INFO',
        #                 'message': "Task '{}' executed".format(task['task'])
        #             })
        #         else:
        #             remaining_tasks.append(task)
        #     if remaining_tasks:
        #         vm.model['tasks'] = remaining_tasks
        #     else:
        #         del vm.model['tasks']
        #     fvm.save(vm)

        # if entries:
        #     vm_infos[vmid]['$pushAll'] = {
        #         'activityLog': entries
        #     }

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
