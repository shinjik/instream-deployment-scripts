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

for tonomi_app_name in args.get('instances', {}).keys():

  try:
    app = marathon_client.get_app(tonomi_app_name)

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
          'link': 'http://{}:{}'.format(marathon_url.split(':')[1], service_port),
          'load-balancer-port': str(service_port),
          'hosts': hosts
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

    app_statuses[tonomi_app_name] = {
      'instanceId': tonomi_app_name,
      'name': tonomi_app_name,
      'status': status,
      'interfaces': interfaces,
      'components': components,
    }
  except:
    app_statuses[tonomi_app_name] = {
      'status': {
        'flags': {
          'active': False,
          'converging': False,
          'failed': False
        }
      }
    }

yaml.safe_dump({'instances': app_statuses}, sys.stdout)
