#!/usr/bin/env python3

from yaml.representer import SafeRepresenter
from marathon import MarathonClient
import datetime
import sys
import yaml

args = yaml.safe_load(sys.stdin)
marathon_url = args.get('configuration', {}).get('configuration.marathonURL')
marathon_client = MarathonClient(marathon_url)

app_statuses = {}

for instance_name in sorted(list(args.get('instances', {}).keys())):
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
    port_mappings = {pm.container_port: pm.service_port for pm in app.container.docker.port_mappings}

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

    app_statuses[instance_name] = {
      'instanceId': instance_name,
      'name': instance_name,
      'status': status,
      'interfaces': interfaces,
      'components': {},
    }

  except:
    app_statuses[instance_name] = {
      'status': {
        'flags': {
          'active': False,
          'converging': False,
          'failed': False
        }
      }
    }

yaml.safe_dump({'instances': app_statuses}, sys.stdout)
