#!/usr/bin/env python3

import sys
import json
import requests
import yaml
from marathon import MarathonClient
from marathon.models import MarathonApp
from marathon.models.container import *
from lambdas import *

args = parse_args()
marathon_client = get_marathon_client(args)
instances = {}

for instance_id, app in args['launch-instances'].items():
  conf = lambda x, app=app: app.get('configuration')['configuration.{}'.format(x)]
  instance_name = conf('name')

  if conf('group') and conf('group') != '':
    instance_name = '/{}{}'.format(conf('group'), instance_name)

  port_mappings = []
  for port in conf('portMappings'):
    port_mapping_opts = {
      'container_port': int(port['containerPort']),
      'host_port': int(port['hostPort']),
      'service_port': int(port['servicePort']),
      'protocol': 'tcp'
    }
    port_mappings.append(MarathonContainerPortMapping(**port_mapping_opts))

  docker_opts = {
    'network': 'BRIDGE',
    'image': conf('imageId'),
    'port_mappings': port_mappings
  }

  app_opts = {
    'id': instance_name,
    'cmd': conf('cmd'),
    'cpus': float(conf('cpu')),
    'mem': conf('ram'),
    'disk': conf('disk'),
    'instances': conf('instances'),
    'labels': conf('labels'),
    'container': MarathonContainer(docker=MarathonDockerContainer(**docker_opts))
  }

  marathon_client.create_app(instance_name, MarathonApp(**app_opts))

  instances[instance_name] = {
    'instanceId': instance_id,
    '$set': {
      'status.flags.converging': True,
      'status.flags.active': False
    }
  }

return_instances_info(instances)
