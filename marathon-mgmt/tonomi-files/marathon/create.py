#!/usr/bin/env python3

import sys
import json
import requests
import yaml
from marathon import MarathonClient
from marathon.models import MarathonApp
from marathon.models.container import *


args = yaml.safe_load(sys.stdin)
marathon_url = args.get('configuration', {}).get('configuration.marathonURL')

marathon_client = MarathonClient(marathon_url)

instance_results = {}

for tonomi_instance_id, app in args.get('launch-instances', {}).items():
  configuration = app.get('configuration')
  tonomi_instance_name = configuration['configuration.name']
  tonomi_env_name = 'sandbox'
  try:
    tonomi_env_name = tonomi_instance_name.split('/')[1]
  except:
    tonomi_instance_name = '/{}/{}'.format(tonomi_env_name, tonomi_instance_name)

  port_mappings = []
  for p in configuration['configuration.portMappings']:
    port_mappings.append({
      MarathonContainerPortMapping(name=None, container_port=int(list(p.keys())[0]), host_port=0,
                                   service_port=int(p[list(p.keys())[0]]), protocol='tcp', labels={})
    })

  cmd = configuration['configuration.cmd']
  cpus = float(configuration['configuration.cpu'])
  mem = int(configuration['configuration.ram'])
  disk = int(configuration['configuration.disk'])
  instances = int(configuration['configuration.instances'])
  image = configuration['configuration.imageId']

  docker = MarathonDockerContainer(image=image, network='BRIDGE', port_mappings=port_mappings,
                                   parameters=[], privileged=False, force_pull_image=False)
  container = MarathonContainer(docker=docker)

  labels = {
    '_tonomi_marathon_instance_id': tonomi_instance_id,
    '_tonomi_environment': tonomi_env_name
  }

  new_marathon_app = MarathonApp(id=tonomi_instance_name, cmd=cmd, cpus=cpus, mem=mem, instances=instances, disk=disk,
                                 labels=labels, container=container)

  marathon_client.create_app(tonomi_instance_name, new_marathon_app)

  instance_results[tonomi_instance_name] = {
    'instanceId': tonomi_instance_id,
    '$set': {
      'status.flags.converging': True,
      'status.flags.active': False
    }
  }

yaml.safe_dump({'instances': instance_results}, sys.stdout)
