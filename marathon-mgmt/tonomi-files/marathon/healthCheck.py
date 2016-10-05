#!/usr/bin/env python3

import sys
import yaml
import datetime
import requests



from collections import defaultdict
from yaml.representer import SafeRepresenter

# to serialize defaultdicts normally
SafeRepresenter.add_representer(defaultdict, SafeRepresenter.represent_dict)

arguments = yaml.safe_load(sys.stdin)

app_ids = list(arguments.get('instances', {}).keys())
marathon_url = arguments.get('configuration', {}).get('configuration.marathonURL', 'http://localhost:8080')


def multidict():
    return defaultdict(multidict)

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

def info(url, id, debug):
    res = None
    try:
        res = make_request('GET', url + "/v2/apps" + id)
        a = res['app']
        return a
    except Exception:
        return None


app_infos = {}
for appid in app_ids:
    app = info(marathon_url, appid, False)
    if app:
        status = {
            'flags': {
                'active': True,
                'converging': False,
                'failed': app['tasksUnhealthy'] > 0 #bool(vm.model.get('failure'))
            }
        }
        #if 'failure' in vm.model:
        #    status['message'] = vm.model['failure']
        tasks = []
        for task in app['tasks']:
            
            t = {
                    'taskId': task['id'],
                    'host': task['host'],
                    #'ports': str(task['ports']),

                    'state': task['state']
                    



                }
            if app['container'].get('docker', None):
                t['portMappings'] = { p['containerPort']: task['ports'][i] for i,p in enumerate(app['container']['docker']['portMappings'])}
            else:
                t['ports'] = task['ports']
            tasks.append(t)
        port_mappings = {str(p['containerPort']): str(p['servicePort']) for p in app['container']['docker']['portMappings']}
        interfaces = {
            'info': {
                'signals': {
                    'app-id': app['id'],
                    'ram': app['mem'],
                    'cpu': app['cpus'],
                    'num_instances': app['instances']
                }
            },
            'compute': {
                'signals': {
                    'ram': app['mem'],
                    'cpu': app['cpus'],
                    'instances': app['instances'],
                    'portMappings': port_mappings
                }
            },
            'instances': {
                'signals':  {
                    'tasks': tasks
                }
            }
        }

        # if 'address' in vm.model:
        #     interfaces['info']['signals']['address'] = vm.model['address']

        # if 'login' in vm.model:
        #     interfaces['info']['signals']['login'] = vm.model['login']

        components = multidict()
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
            'instanceId': app['id'],
            'name': app['id'],
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
