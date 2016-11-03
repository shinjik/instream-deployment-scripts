#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient
from lambdas import *

args = parse_args()
marathon_client = get_marathon_client(args)
instances = {}

for instance_name in args['instances'].keys():

  # try:
    app = marathon_client.get_app(instance_name)

    status = {
      'flags': {
        'active': True,
        'converging': False,
        'failed': app.tasks_unhealthy > 0
      }
    }

    service_port = app.container.docker.port_mappings[0].service_port
    hosts = [task.host for task in app.tasks]

    interfaces = {
      'compute': {
        'signals': {
          'ram': app.mem * app.tasks_running,
          'cpu': app.cpus * app.tasks_running,
          'disk': app.disk * app.tasks_running,
          'instances': app.tasks_running
        }
      },
      'ui': {
        'signals': {
          'link': 'http://{}:{}'.format(marathon_client.servers[0].split(':')[1][2:], service_port),
          'load-balancer-port': str(service_port),
          'hosts': hosts
        }
      }
    }

    components = {}
    components['ui'] = {
      'reference': {
        'mapping': 'apps.app-by-id',
        'key': app.id
      }
    }

    instances[instance_name] = {
      'instanceId': instance_name,
      'name': instance_name,
      'status': status,
      'interfaces': interfaces,
      'components': components,
    }
  # except:
  #   app_statuses[tonomi_app_name] = {
  #     'status': {
  #       'flags': {
  #         'active': False,
  #         'converging': False,
  #         'failed': False
  #       }
  #     }
  #   }

return_instances_info(instances)
