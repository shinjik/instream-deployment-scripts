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

  try:
    app = marathon_client.get_app(tonomi_cluster_instance_name)

    status = {
      'flags': {
        'active': True,
        'converging': False,
        'failed': app.tasks_unhealthy > 0
      }
    }

    interfaces = {
      'compute': {
        'signals': {
          'ram': app.mem * app.tasks_running,
          'cpu': app.cpus * app.tasks_running,
          'disk': app.disk * app.tasks_running,
          'instances': app.tasks_running
        }
      },
      'kafka': {
        'signals': {
          'kafka-hosts': [task.host for task in app.tasks],
          'kafka-port': app.env['KAFKA_PORT']
        }
      }
    }

    components = multidict()
    components['kafka-broker'] = {
      'reference': {
        'mapping': 'apps.app-by-id',
        'key': app.id
      }
    }

    app_statuses[tonomi_cluster_instance_name] = {
      'instanceId': tonomi_cluster_instance_name,
      'name': tonomi_cluster_instance_name,
      'status': status,
      'interfaces': interfaces,
      'components': components,
    }
  except:
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
