#!/usr/bin/env python3

import sys
import yaml
import datetime
from collections import defaultdict
from yaml.representer import SafeRepresenter
from marathon import MarathonClient


# to serialize defaultdicts normally
SafeRepresenter.add_representer(defaultdict, SafeRepresenter.represent_dict)
def multidict():
  return defaultdict(multidict)


args = yaml.safe_load(sys.stdin)

marathon_url = args.get('configuration', {}).get('configuration.marathonURL', '')

marathon_client = MarathonClient(marathon_url)

app_statuses = {}

for tonomi_instance_name in args.get('instances', {}).keys():
  try:
    app = marathon_client.get_app(tonomi_instance_name)
    if '_tonomi_environment' not in app.labels or '_tonomi_application' not in app.labels:
      raise Exception

    status = {
      'flags': {
        'active': True,
        'converging': False,
        'failed': app.tasks_unhealthy > 0
      }
    }

    tasks = []
    for task in app.tasks:
      t = {
        'taskId': task.id,
        'host': task.host,
        'state': task.state
      }
      # if app.container.docker:
      #   t['portMappings'] = { str(p.container_port): str(task.ports) for p in app.container.docker.port_mappings }
      # else:
      #   t['ports'] = task.ports
      tasks.append(t)

    port_mappings = { str(p.container_port): str(p.service_port) for p in app.container.docker.port_mappings }
    interfaces = {
      'info': {
        'signals': {
          'app-id': app.id,
          'ram': app.mem,
          'cpu': app.cpus,
          'num_instances': app.instances
        }
      },
      'compute': {
        'signals': {
          'ram': app.mem,
          'cpu': app.cpus,
          'instances': app.instances,
          'portMappings': port_mappings
        }
      },
      'instances': {
        'signals': {
          'tasks': tasks
        }
      }
    }

    components = multidict()

    app_statuses[tonomi_instance_name] = {
      'instanceId': tonomi_instance_name,
      'name': tonomi_instance_name,
      'status': status,
      'interfaces': interfaces,
      'components': components,
    }

  except:
    app_statuses[tonomi_instance_name] = {
      'status': {
        'flags': {
          'active': False,
          'converging': False,
          'failed': False
        }
      }
    }

yaml.safe_dump({ 'instances': app_statuses }, sys.stdout)
