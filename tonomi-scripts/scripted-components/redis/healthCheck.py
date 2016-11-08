#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient
from lambdas import *
from models import *

args = parse_args()
marathon_client = get_marathon_client(args)
instances = {}

for instance_name in args['instances'].keys():
  try:
    master_app = marathon_client.get_app('{}/redis-master'.format(instance_name))
    slave_app = marathon_client.get_app('{}/redis-slave'.format(instance_name))

    # check that master-slave connection is ok
    master_host = master_app.tasks[0].host
    new_cmd = 'docker-entrypoint.sh redis-server --port $REDIS_PORT --slaveof {} $REDIS_PORT'.format(master_host)
    if new_cmd != slave_app.cmd:
      slave_app.cmd = new_cmd
      marathon_client.update_app(slave_app.id, slave_app, True)

    status = {
      'flags': {
        'active': True,
        'converging': False,
        'failed': master_app.tasks_unhealthy > 0
      }
    }

    master_tasks_running = master_app.tasks_running
    slave_tasks_running = slave_app.tasks_running

    interfaces = {
      'compute': {
        'signals': {
          'ram': master_app.mem * master_tasks_running + slave_app.mem * slave_tasks_running,
          'cpu': master_app.cpus * master_tasks_running + slave_app.cpus * slave_tasks_running,
          'disk': master_app.disk * master_tasks_running + slave_app.disk * slave_tasks_running
        }
      },
      'redis': {
        'signals': {
          'master-hosts': [master_task.host for master_task in master_app.tasks],
          'slave-hosts': [slave_task.host for slave_task in slave_app.tasks]
        }
      }
    }

    components = {
      'redis-master': {
        'reference': {
          'mapping': 'apps.app-by-id',
          'key': '{}/redis-master'.format(instance_name)
        }
      },
      'redis-slave': {
        'reference': {
          'mapping': 'apps.app-by-id',
          'key': '{}/redis-slave'.format(instance_name)
        }
      }
    }

    instances[instance_name] = {
      'instanceId': instance_name,
      'name': instance_name,
      'status': status,
      'interfaces': interfaces,
      'components': components,
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
