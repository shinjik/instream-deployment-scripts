#!/usr/bin/env python3

import sys
import yaml
from collections import defaultdict
from yaml.representer import SafeRepresenter
from marathon import MarathonClient

# to serialize defaultdicts normally
SafeRepresenter.add_representer(defaultdict, SafeRepresenter.represent_dict)


def multidict():
  return defaultdict(multidict)


args = yaml.safe_load(sys.stdin)
marathon_url = args.get('configuration', {}).get('configuration.marathonURL')
marathon_client = MarathonClient(marathon_url)

app_statuses = {}

for tonomi_cluster_instance_name in args.get('instances', {}).keys():
  env_name = tonomi_cluster_instance_name.split('/')[1]

  cluster_exist = False
  list_apps = marathon_client.list_apps()
  for app in list_apps:
    if app.id == '/{}/redis-master'.format(env_name) or app.id == '/{}/redis-slave'.format(env_name):
      cluster_exist = True

  if cluster_exist:
    master_app = marathon_client.get_app('/{}/redis-master'.format(env_name))
    slave_app = marathon_client.get_app('/{}/redis-slave'.format(env_name))

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

    components = multidict()
    components['redis-master'] = {
      'reference': {
        'mapping': 'apps.app-by-id',
        'key': '/{}/redis-master'.format(env_name)
      }
    }
    components['redis-slave'] = {
      'reference': {
        'mapping': 'apps.app-by-id',
        'key': '/{}/redis-slave'.format(env_name)
      }
    }

    app_statuses[tonomi_cluster_instance_name] = {
      'instanceId': tonomi_cluster_instance_name,
      'name': tonomi_cluster_instance_name,
      'status': status,
      'interfaces': interfaces,
      'components': components,
    }

  else:
    app_statuses[tonomi_cluster_instance_name] = {
      'status': {
        'flags': {
          'active': False,
          'converging': False,
          'failed': False
        }
      }
    }

yaml.safe_dump({'instances': app_statuses}, sys.stdout)
