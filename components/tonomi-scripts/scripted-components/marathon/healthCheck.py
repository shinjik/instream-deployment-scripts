#!/usr/bin/env python3

import datetime
import sys
import yaml
from marathon import MarathonClient
from utils import *

args = parse_args()
marathon_client = get_marathon_client(args)
instances = {}

for instance_name in sorted(list(args['instances'].keys())):
  try:
    app = marathon_client.get_app(instance_name)

    status = {
      'flags': {
        'active': True,
        'converging': False,
        'failed': app.tasks_unhealthy > 0
      }
    }

    tasks = [{'taskId': task.id, 'host': task.host, 'state': task.state} for task in app.tasks]
    port_mappings = [{'containerPort': pm.container_port, 'hostPort': pm.host_port, 'servicePort': pm.service_port} for pm in app.container.docker.port_mappings]

    interfaces = {
      'compute': {
        'signals': {
          'ram': app.mem,
          'cpu': str(app.cpus),
          'disk': app.disk,
          'instances': app.instances,
          'portMappings': port_mappings,
          'labels': app.labels
        }
      },
      'instances': {
        'signals': {
          'tasks': tasks
        }
      }
    }

    instances[instance_name] = {
      'instanceId': instance_name,
      'name': instance_name,
      'status': status,
      'interfaces': interfaces,
      'components': {}
    }

  except:
    instances[instance_name] = {
      'status': {
        'flags': {
          'active': False,
          'converging': False,
          'failed': False
        }
      }
    }

return_instances_info(instances)
